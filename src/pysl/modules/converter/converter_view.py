from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from pysl.modules.converter.service import CodeConverter


class ConverterView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._converter = CodeConverter()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        title = QLabel("Convertidor de código")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Convierte entre PySL y Python. Python → PySL cubre estructuras educativas comunes."
        )
        subtitle.setObjectName("subtitle")
        controls = QHBoxLayout()
        self._direction = QComboBox()
        self._direction.addItems(["PySL → Python", "Python → PySL"])
        button = QPushButton("Convertir")
        button.clicked.connect(self._convert)
        swap = QPushButton("Intercambiar")
        swap.setObjectName("secondaryButton")
        swap.clicked.connect(self._swap)
        controls.addWidget(self._direction)
        controls.addWidget(button)
        controls.addWidget(swap)
        controls.addStretch()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._source = QPlainTextEdit('inicio\nimprimir("Hola PySL")\nfin')
        self._source.setObjectName("codeEditor")
        self._target = QPlainTextEdit()
        self._target.setObjectName("codeEditor")
        splitter.addWidget(self._source)
        splitter.addWidget(self._target)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(controls)
        root.addWidget(splitter, 1)

    def _convert(self) -> None:
        try:
            source = self._source.toPlainText()
            if self._direction.currentIndex() == 0:
                result = self._converter.pysl_to_python(source)
            else:
                result = self._converter.python_to_pysl(source)
            self._target.setPlainText(result)
        except Exception as exc:
            QMessageBox.critical(self, "Error de conversión", str(exc))

    def _swap(self) -> None:
        left, right = self._source.toPlainText(), self._target.toPlainText()
        self._source.setPlainText(right)
        self._target.setPlainText(left)
        self._direction.setCurrentIndex(1 - self._direction.currentIndex())
