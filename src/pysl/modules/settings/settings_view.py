from PySide6.QtWidgets import (
    QApplication,
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
from pysl.ui.styles import (
    DARK_THEME,
    DEFAULT_FONT_SIZE,
    LIGHT_THEME,
    apply_theme,
    normalize_theme,
)


class SettingsView(QWidget):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__()
        self.db = database or Database()
        root = QVBoxLayout(self)

        title = QLabel("Configuración")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Personaliza la apariencia de PySL. Los cambios se aplican al guardar.")
        subtitle.setObjectName("subtitle")

        form = QFormLayout()
        self.theme = QComboBox()
        self.theme.addItems([DARK_THEME, LIGHT_THEME])
        self.theme.setCurrentText(normalize_theme(self.db.get_preference("theme", DARK_THEME)))

        self.font_size = QSpinBox()
        self.font_size.setRange(11, 24)
        self.font_size.setValue(self._stored_font_size())

        form.addRow("Tema", self.theme)
        form.addRow("Tamaño de fuente", self.font_size)

        save = QPushButton("Guardar configuración")
        save.clicked.connect(self._save)

        reset = QPushButton("Restablecer progreso y preferencias")
        reset.setObjectName("dangerButton")
        reset.clicked.connect(self._reset)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(form)
        root.addWidget(save)
        root.addWidget(reset)
        root.addStretch()

    def _save(self) -> None:
        selected_theme = normalize_theme(self.theme.currentText())
        selected_font_size = self.font_size.value()

        self.db.set_preference("theme", selected_theme)
        self.db.set_preference("font_size", str(selected_font_size))
        self._apply_preferences(selected_theme, selected_font_size)

        QMessageBox.information(
            self,
            "Configuración",
            "Las preferencias se guardaron y se aplicaron correctamente.",
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
        self.theme.setCurrentText(DARK_THEME)
        self.font_size.setValue(DEFAULT_FONT_SIZE)
        self._apply_preferences(DARK_THEME, DEFAULT_FONT_SIZE)
        QMessageBox.information(self, "Progreso", "El progreso y las preferencias se restablecieron.")

    def _stored_font_size(self) -> int:
        try:
            value = int(self.db.get_preference("font_size", str(DEFAULT_FONT_SIZE)))
        except ValueError:
            return DEFAULT_FONT_SIZE
        return max(11, min(24, value))

    @staticmethod
    def _apply_preferences(theme: str, font_size: int) -> None:
        application = QApplication.instance()
        if application is not None:
            apply_theme(application, theme, font_size)
