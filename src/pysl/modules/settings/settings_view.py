from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pysl.core.database import Database


class SettingsView(QWidget):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__()
        self.db = database or Database()
        root = QVBoxLayout(self)
        title = QLabel("Configuración")
        title.setObjectName("pageTitle")
        form = QFormLayout()
        self.theme = QComboBox()
        self.theme.addItems(["Oscuro", "Claro"])
        stored_theme = self.db.get_preference("theme", "Oscuro")
        self.theme.setCurrentText(stored_theme if stored_theme in {"Oscuro", "Claro"} else "Oscuro")
        self.font_size = QSpinBox()
        self.font_size.setRange(11, 24)
        self.font_size.setValue(self._stored_font_size())
        form.addRow("Tema", self.theme)
        form.addRow("Tamaño del editor", self.font_size)
        save = QPushButton("Guardar configuración")
        save.clicked.connect(self._save)
        reset = QPushButton("Restablecer progreso")
        reset.setObjectName("dangerButton")
        reset.clicked.connect(self._reset)
        root.addWidget(title)
        root.addLayout(form)
        root.addWidget(save)
        root.addWidget(reset)
        root.addStretch()

    def _save(self) -> None:
        self.db.set_preference("theme", self.theme.currentText())
        self.db.set_preference("font_size", str(self.font_size.value()))
        QMessageBox.information(
            self,
            "Configuración",
            "Preferencias guardadas. Se aplicarán completamente al reiniciar.",
        )

    def _reset(self) -> None:
        answer = QMessageBox.question(
            self,
            "Restablecer progreso",
            "Se eliminarán el progreso, las estadísticas y las preferencias locales. "
            "¿Deseas continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        self.db.reset()
        QMessageBox.information(self, "Progreso", "El progreso fue restablecido.")

    def _stored_font_size(self) -> int:
        try:
            value = int(self.db.get_preference("font_size", "14"))
        except ValueError:
            return 14
        return max(11, min(24, value))
