from __future__ import annotations

from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSplitter, QVBoxLayout, QWidget, QPlainTextEdit
from PySide6.QtCore import Qt
from pysl.language.executor import PySLExecutor
from pysl.modules.editor.code_editor import CodeEditor
from pysl.modules.editor.highlighter import PySLHighlighter

SAMPLE = '''// Programa PySL 1.0
inicio
entero numero
leer(numero)
si numero % 2 == 0 entonces
    imprimir("El número es par")
sino
    imprimir("El número es impar")
finsi
fin
'''

class EditorView(QWidget):
    def __init__(self) -> None:
        super().__init__(); self.executor = PySLExecutor(); self.current_path: Path | None = None
        root = QVBoxLayout(self)
        title = QLabel("IDE PySL"); title.setObjectName("pageTitle")
        toolbar = QHBoxLayout()
        for text, slot in (("Nuevo", self._new),("Abrir", self._open),("Guardar", self._save),("Guardar como", self._save_as),("▶ Ejecutar", self._run)):
            button = QPushButton(text); button.clicked.connect(slot); toolbar.addWidget(button)
        toolbar.addStretch()
        self.inputs = QLineEdit(); self.inputs.setPlaceholderText("Entradas separadas por coma, por ejemplo: 8, Jairo")
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.editor = CodeEditor(); self.editor.setObjectName("codeEditor"); self.editor.setPlainText(SAMPLE); self.highlighter = PySLHighlighter(self.editor.document())
        self.console = QPlainTextEdit(); self.console.setObjectName("console"); self.console.setReadOnly(True); self.console.setPlaceholderText("Salida del programa")
        splitter.addWidget(self.editor); splitter.addWidget(self.console); splitter.setSizes([520, 220])
        root.addWidget(title); root.addLayout(toolbar); root.addWidget(self.inputs); root.addWidget(splitter, 1)
    def _new(self) -> None: self.current_path = None; self.editor.setPlainText(SAMPLE); self.console.clear()
    def _open(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Abrir programa", "", "PySL (*.pysl);;Todos (*.*)")
        if path: self.current_path = Path(path); self.editor.setPlainText(self.current_path.read_text(encoding="utf-8"))
    def _save(self) -> None:
        if self.current_path is None: return self._save_as()
        self.current_path.write_text(self.editor.toPlainText(), encoding="utf-8")
    def _save_as(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Guardar programa", "main.pysl", "PySL (*.pysl)")
        if path:
            self.current_path = Path(path if path.endswith(".pysl") else path + ".pysl"); self._save()
    def _run(self) -> None:
        try:
            inputs = [value.strip() for value in self.inputs.text().split(",") if value.strip()]
            result = self.executor.execute(self.editor.toPlainText(), inputs)
            self.console.setPlainText(result.output or "Programa finalizado sin salida.")
        except Exception as exc:
            self.console.setPlainText(f"ERROR: {exc}")
