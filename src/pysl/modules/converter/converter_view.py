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
        self._refresh_language_labels()
        self._convert()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        title = QLabel("Convertidor de código")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Convierte entre SL y Python. Python → SL cubre el subconjunto educativo documentado."
        )
        subtitle.setObjectName("subtitle")

        controls = QHBoxLayout()
        self._direction = QComboBox()
        self._direction.addItems(["SL → Python", "Python → SL"])
        self._direction.currentIndexChanged.connect(self._refresh_language_labels)

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

        source_panel = QWidget()
        source_layout = QVBoxLayout(source_panel)
        source_layout.setContentsMargins(0, 0, 0, 0)
        self._source_label = QLabel()
        self._source_label.setObjectName("sectionTitle")
        self._source = QPlainTextEdit('inicio\n    imprimir("Hola desde SL")\nfin')
        self._source.setObjectName("codeEditor")
        source_layout.addWidget(self._source_label)
        source_layout.addWidget(self._source, 1)

        target_panel = QWidget()
        target_layout = QVBoxLayout(target_panel)
        target_layout.setContentsMargins(0, 0, 0, 0)
        self._target_label = QLabel()
        self._target_label.setObjectName("sectionTitle")
        self._target = QPlainTextEdit()
        self._target.setObjectName("codeEditor")
        self._target.setReadOnly(True)
        target_layout.addWidget(self._target_label)
        target_layout.addWidget(self._target, 1)

        splitter.addWidget(source_panel)
        splitter.addWidget(target_panel)
        splitter.setSizes([1, 1])

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(controls)
        root.addWidget(splitter, 1)

    def _refresh_language_labels(self) -> None:
        if self._direction.currentIndex() == 0:
            source_language, target_language = "SL", "Python"
        else:
            source_language, target_language = "Python", "SL"
        self._source_label.setText(f"Código {source_language}")
        self._target_label.setText(f"Código {target_language}")

    def _convert(self) -> None:
        try:
            source = self._source.toPlainText()
            if self._direction.currentIndex() == 0:
                result = self._converter.sl_to_python(source)
            else:
                result = self._converter.python_to_sl(source)
            self._target.setPlainText(result)
        except Exception as exc:
            QMessageBox.critical(self, "Error de conversión", str(exc))

    def _swap(self) -> None:
        source = self._source.toPlainText()
        target = self._target.toPlainText()

        self._direction.setCurrentIndex(1 - self._direction.currentIndex())
        self._source.setPlainText(target)
        self._target.setPlainText(source)
        self._refresh_language_labels()
