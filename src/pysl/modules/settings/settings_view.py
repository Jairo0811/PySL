from PySide6.QtWidgets import QComboBox, QFormLayout, QLabel, QMessageBox, QPushButton, QSpinBox, QVBoxLayout, QWidget
from pysl.core.database import Database

class SettingsView(QWidget):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__(); self.db = database or Database()
        root = QVBoxLayout(self)
        title = QLabel("Configuración"); title.setObjectName("pageTitle")
        form = QFormLayout()
        self.theme = QComboBox(); self.theme.addItems(["Oscuro", "Claro"]); self.theme.setCurrentText(self.db.get_preference("theme", "Oscuro"))
        self.font_size = QSpinBox(); self.font_size.setRange(11, 24); self.font_size.setValue(int(self.db.get_preference("font_size", "14")))
        form.addRow("Tema", self.theme); form.addRow("Tamaño del editor", self.font_size)
        save = QPushButton("Guardar configuración"); save.clicked.connect(self._save)
        reset = QPushButton("Restablecer progreso"); reset.setObjectName("dangerButton"); reset.clicked.connect(self._reset)
        root.addWidget(title); root.addLayout(form); root.addWidget(save); root.addWidget(reset); root.addStretch()
    def _save(self) -> None:
        self.db.set_preference("theme", self.theme.currentText()); self.db.set_preference("font_size", str(self.font_size.value()))
        QMessageBox.information(self, "Configuración", "Preferencias guardadas. Se aplicarán completamente al reiniciar.")
    def _reset(self) -> None:
        self.db.reset(); QMessageBox.information(self, "Progreso", "El progreso fue restablecido.")
