from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QThreadPool
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
        self.highlighter = SLHighlighter(self.editor.document())
        self.console = QPlainTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setPlaceholderText("Salida del programa SL")
        splitter.addWidget(self.editor)
        splitter.addWidget(self.console)
        splitter.setSizes([520, 220])

        root.addWidget(title)
        root.addLayout(toolbar)
        root.addWidget(self.inputs)
        root.addWidget(splitter, 1)

    def _new(self) -> None:
        self.current_path = None
        self.editor.setPlainText(SAMPLE)
        self.console.clear()

    def _open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir programa SL",
            "",
            "Programas SL (*.pysl);;Todos los archivos (*.*)",
        )
        if not path:
            return
        try:
            self.current_path = Path(path)
            self.editor.setPlainText(self.current_path.read_text(encoding="utf-8"))
        except OSError as exc:
            QMessageBox.critical(self, "No se pudo abrir el archivo", str(exc))

    def _save(self) -> None:
        if self.current_path is None:
            self._save_as()
            return
        try:
            self.current_path.write_text(self.editor.toPlainText(), encoding="utf-8")
        except OSError as exc:
            QMessageBox.critical(self, "No se pudo guardar el archivo", str(exc))

    def _save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar programa SL",
            "main.pysl",
            "Programas SL (*.pysl)",
        )
        if not path:
            return
        self.current_path = Path(path if path.casefold().endswith(".pysl") else f"{path}.pysl")
        self._save()

    def _run(self) -> None:
        if self._execution_task is not None:
            return
        inputs = [value.strip() for value in self.inputs.text().split(",") if value.strip()]
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
        self.console.setPlainText(result.output or "Programa finalizado sin salida.")

    def _execution_failed(self, message: str) -> None:
        self.console.setPlainText(f"ERROR: {message}")

    def _execution_completed(self) -> None:
        self._execution_task = None
        self._run_button.setEnabled(True)
        self._run_button.setText("▶ Ejecutar")
