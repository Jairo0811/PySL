from PySide6.QtGui import QHideEvent
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
    MAX_FONT_SIZE,
    MIN_FONT_SIZE,
    apply_theme,
    normalize_theme,
    parse_font_size,
)


class SettingsView(QWidget):
    def __init__(self, database: Database | None = None) -> None:
        super().__init__()
        self.db = database or Database()
        root = QVBoxLayout(self)

        title = QLabel("Configuración")
        title.setObjectName("pageTitle")
        subtitle = QLabel(
            "Personaliza la apariencia de PySL. El tema y el tamaño se previsualizan al "
            "instante; guarda la configuración para conservarlos."
        )
        subtitle.setObjectName("subtitle")

        form = QFormLayout()
        self._saved_theme = normalize_theme(self.db.get_preference("theme", DARK_THEME))
        self._saved_font_size = self._stored_font_size()

        self.theme = QComboBox()
        self.theme.addItems([DARK_THEME, LIGHT_THEME])
        self.theme.setCurrentText(self._saved_theme)

        self.font_size = QSpinBox()
        self.font_size.setRange(MIN_FONT_SIZE, MAX_FONT_SIZE)
        self.font_size.setValue(self._saved_font_size)

        self.theme.currentTextChanged.connect(self._preview_preferences)
        self.font_size.valueChanged.connect(self._preview_preferences)

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

    def hideEvent(self, event: QHideEvent) -> None:
        """Undo an unsaved preview when the student leaves the page."""
        super().hideEvent(event)
        if not event.spontaneous():
            self._discard_unsaved_preview()

    def _discard_unsaved_preview(self) -> None:
        if (
            normalize_theme(self.theme.currentText()) == self._saved_theme
            and self.font_size.value() == self._saved_font_size
        ):
            return
        for control in (self.theme, self.font_size):
            control.blockSignals(True)
        self.theme.setCurrentText(self._saved_theme)
        self.font_size.setValue(self._saved_font_size)
        for control in (self.theme, self.font_size):
            control.blockSignals(False)
        self._apply_preferences(self._saved_theme, self._saved_font_size)

    def _preview_preferences(self, _value: object = None) -> None:
        self._apply_preferences(normalize_theme(self.theme.currentText()), self.font_size.value())

    def _save(self) -> None:
        selected_theme = normalize_theme(self.theme.currentText())
        selected_font_size = self.font_size.value()

        self.db.set_preference("theme", selected_theme)
        self.db.set_preference("font_size", str(selected_font_size))
        self._saved_theme = selected_theme
        self._saved_font_size = selected_font_size
        self._apply_preferences(selected_theme, selected_font_size)

        QMessageBox.information(
            self,
            "Configuración",
            "Las preferencias se guardaron correctamente.",
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
        self._saved_theme = DARK_THEME
        self._saved_font_size = DEFAULT_FONT_SIZE
        self.theme.setCurrentText(DARK_THEME)
        self.font_size.setValue(DEFAULT_FONT_SIZE)
        self._apply_preferences(DARK_THEME, DEFAULT_FONT_SIZE)
        QMessageBox.information(
            self, "Progreso", "El progreso y las preferencias se restablecieron."
        )

    def _stored_font_size(self) -> int:
        return parse_font_size(self.db.get_preference("font_size", str(DEFAULT_FONT_SIZE)))

    @staticmethod
    def _apply_preferences(theme: str, font_size: int) -> None:
        application = QApplication.instance()
        if application is not None:
            apply_theme(application, theme, font_size)
