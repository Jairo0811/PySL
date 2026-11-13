from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from pysl.language.executor import ExecutionResult
from pysl.modules.editor.code_editor import CodeEditor
from pysl.modules.editor.execution_task import ExecutionTask
from pysl.modules.editor.highlighter import SLHighlighter

SAMPLE = """// Programa SL 1.0
inicio
entero numero
leer(numero)
si numero % 2 == 0 entonces
    imprimir("El número es par")
sino
    imprimir("El número es impar")
finsi
fin
"""


class EditorView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_path: Path | None = None
        self._execution_task: ExecutionTask | None = None

        root = QVBoxLayout(self)
        title = QLabel("IDE de SL")
        title.setObjectName("pageTitle")
        self.file_label = QLabel()
        self.file_label.setObjectName("subtitle")

        toolbar = QHBoxLayout()
        actions = (
            ("Nuevo", self._new),
            ("Abrir", self._open),
            ("Guardar", self._save),
            ("Guardar como", self._save_as),
        )
        for text, slot in actions:
            button = QPushButton(text)
            button.clicked.connect(slot)
            toolbar.addWidget(button)
        self._run_button = QPushButton("▶ Ejecutar")
        self._run_button.clicked.connect(self._run)
        toolbar.addWidget(self._run_button)
        toolbar.addStretch()

        self.inputs = QLineEdit()
        self.inputs.setPlaceholderText("Entradas separadas por coma, por ejemplo: 8, Jairo")
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.editor = CodeEditor()
        self.editor.setObjectName("codeEditor")
        self.editor.setPlainText(SAMPLE)
        self.editor.document().setModified(False)
        self.editor.document().modificationChanged.connect(self._update_file_label)
        self.highlighter = SLHighlighter(self.editor.document())
        self.console = QPlainTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Salida del programa SL")
        splitter.addWidget(self.editor)
        splitter.addWidget(self.console)
        splitter.setSizes([520, 220])

        root.addWidget(title)
        root.addWidget(self.file_label)
        root.addLayout(toolbar)
        root.addWidget(self.inputs)
        root.addWidget(splitter, 1)

        self._install_shortcuts()
        self._update_file_label()

    def _install_shortcuts(self) -> None:
        bindings = (
            (QKeySequence.StandardKey.New, self._new),
            (QKeySequence.StandardKey.Open, self._open),
            (QKeySequence.StandardKey.Save, self._save),
            (QKeySequence("Ctrl+Shift+S"), self._save_as),
            (QKeySequence("F5"), self._run),
            (QKeySequence("Ctrl+Return"), self._run),
        )
        for sequence, slot in bindings:
            shortcut = QShortcut(sequence, self)
            shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            shortcut.activated.connect(slot)

    def _update_file_label(self, *_: object) -> None:
        name = self.current_path.name if self.current_path else "Sin título"
        marker = " *" if self.editor.document().isModified() else ""
        self.file_label.setText(f"{name}{marker}")

    def confirm_discard(self) -> bool:
        """Ask what to do with unsaved changes; return False when the user cancels."""
        if not self.editor.document().isModified():
            return True
        answer = QMessageBox.question(
            self,
            "Cambios sin guardar",
            "El programa tiene cambios sin guardar. ¿Deseas guardarlos antes de continuar?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save,
        )
        if answer == QMessageBox.StandardButton.Cancel:
            return False
        if answer == QMessageBox.StandardButton.Save:
            return self._save()
        return True

    def _load_text(self, text: str, path: Path | None) -> None:
        self.current_path = path
        self.editor.setPlainText(text)
        self.editor.document().setModified(False)
        self.console.clear()
        self._update_file_label()

    def _new(self) -> None:
        if not self.confirm_discard():
            return
        self._load_text(SAMPLE, None)

    def _open(self) -> None:
        if not self.confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir programa SL",
            "",
            "Programas SL (*.pysl);;Todos los archivos (*.*)",
        )
        if not path:
            return
        # Read first: a failed read must not leave ``current_path`` pointing at that file,
        # otherwise "Guardar" would overwrite it with the previous program.
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            QMessageBox.critical(self, "No se pudo abrir el archivo", str(exc))
            return
        self._load_text(text, Path(path))

    def _save(self) -> bool:
        if self.current_path is None:
            return self._save_as()
        try:
            self.current_path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, "No se pudo guardar el archivo", str(exc))
            return False
        self.editor.document().setModified(False)
        self._update_file_label()
        return True

    def _save_as(self) -> bool:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar programa SL",
            "main.pysl",
            "Programas SL (*.pysl)",
        )
        if not path:
            return False
        previous_path = self.current_path
        self.current_path = Path(path if path.casefold().endswith(".pysl") else f"{path}.pysl")
        if not self._save():
            self.current_path = previous_path
            self._update_file_label()
            return False
        return True

    def _run(self) -> None:
        if self._execution_task is not None:
            return
        inputs = [value.strip() for value in self.inputs.text().split(",") if value.strip()]
        self.editor.clear_error_line()
        task = ExecutionTask(self.editor.toPlainText(), inputs)
        task.signals.succeeded.connect(self._execution_succeeded)
        task.signals.failed.connect(self._execution_failed)
        task.signals.completed.connect(self._execution_completed)
        self._execution_task = task
        self._run_button.setEnabled(False)
        self._run_button.setText("Ejecutando…")
        self.console.setPlainText("Ejecutando el programa SL en un proceso aislado…")
        QThreadPool.globalInstance().start(task)

    def _execution_succeeded(self, result: ExecutionResult) -> None:
        self.editor.clear_error_line()
        self.console.setPlainText(result.output or "Programa finalizado sin salida.")

    def _execution_failed(self, message: str, line: int) -> None:
        # Runtime messages already start with "Error de ejecución:"; avoid "ERROR: Error …".
        self.console.setPlainText(message if message.startswith("Error") else f"ERROR: {message}")
        if line > 0:
            self.editor.show_error_line(line)

    def _execution_completed(self) -> None:
        self._execution_task = None
        self._run_button.setEnabled(True)
        self._run_button.setText("▶ Ejecutar")
