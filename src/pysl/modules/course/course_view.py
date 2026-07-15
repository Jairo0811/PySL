from PySide6.QtWidgets import QLabel, QListWidget, QPlainTextEdit, QSplitter, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

LESSONS = {
    "1. Variables y tipos": "Aprende numerico, entero, real, cadena, logico y caracter.\n\nEjemplo:\ninicio\nentero edad = 28\nimprimir(edad)\nfin",
    "2. Condicionales": "Usa si, sino y finsi para tomar decisiones.",
    "3. Ciclos": "Repite instrucciones con mientras y para.",
    "4. Vectores": "Agrupa valores con listas e índices.",
    "5. Funciones": "Divide algoritmos con funcion, retornar y finfuncion.",
    "6. Proyecto final": "Combina entrada, decisiones, ciclos, vectores y funciones.",
}

class CourseView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        title = QLabel("Curso de Fundamentos"); title.setObjectName("pageTitle")
        subtitle = QLabel("Ruta compacta para aprender programación estructurada con PySL."); subtitle.setObjectName("subtitle")
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.list = QListWidget(); self.list.addItems(LESSONS)
        self.content = QPlainTextEdit(); self.content.setReadOnly(True)
        self.list.currentTextChanged.connect(lambda key: self.content.setPlainText(LESSONS.get(key, "")))
        splitter.addWidget(self.list); splitter.addWidget(self.content); splitter.setStretchFactor(1, 1)
        root.addWidget(title); root.addWidget(subtitle); root.addWidget(splitter, 1)
        self.list.setCurrentRow(0)
