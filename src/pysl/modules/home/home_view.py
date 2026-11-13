from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QShowEvent
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pysl.core.database import Database
from pysl.core.settings import SETTINGS


class HomeView(QWidget):
    def __init__(
        self,
        username: str,
        navigate: Callable[[str], None],
        database: Database | None = None,
    ) -> None:
        super().__init__()
        self._username = username
        self._navigate = navigate
        self._database = database or Database()
        self._stat_values: dict[str, QLabel] = {}
        self._build_ui()

    def showEvent(self, event: QShowEvent) -> None:
        # The page stays alive in a QStackedWidget, so refresh whenever it becomes visible.
        super().showEvent(event)
        self.refresh_stats()

    def refresh_stats(self) -> None:
        """Reload progress counters from the database."""
        summary = self._database.summary()
        values = {
            "labs": str(summary.completed_labs),
            "played": str(summary.games_played),
            "won": str(summary.games_won),
        }
        for key, text in values.items():
            self._stat_values[key].setText(text)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(18)

        hero = QFrame()
        hero.setObjectName("card")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(34, 28, 34, 28)

        text = QVBoxLayout()
        title = QLabel(f"Bienvenido a PySL, {self._username}")
        title.setObjectName("pageTitle")
        body = QLabel(
            "Aprende programación estructurada con la claridad de SL y el poder "
            "de Python. Continúa tu formación desde el laboratorio, el IDE o el curso."
        )
        body.setObjectName("subtitle")
        body.setWordWrap(True)
        body.setMaximumWidth(700)

        actions = QHBoxLayout()
        start = QPushButton("Comenzar en el IDE")
        start.clicked.connect(lambda: self._navigate("IDE de SL"))
        course = QPushButton("Continuar el curso")
        course.setObjectName("secondaryButton")
        course.clicked.connect(lambda: self._navigate("Curso"))
        actions.addWidget(start)
        actions.addWidget(course)
        actions.addStretch()

        text.addWidget(title)
        text.addWidget(body)
        text.addSpacing(8)
        text.addLayout(actions)
        text.addStretch()

        logo = QLabel()
        pixmap = QPixmap(str(SETTINGS.assets_dir / "pysl-logo.png"))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    225,
                    225,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hero_layout.addLayout(text, 3)
        hero_layout.addWidget(logo, 1)

        stats_data = (
            ("labs", "0", "Laboratorios completados"),
            ("played", "0", "Partidas jugadas"),
            ("won", "0", "Victorias"),
            ("version", SETTINGS.version, "Versión estable"),
        )
        stats = QGridLayout()
        stats.setHorizontalSpacing(14)
        for column, (key, value, label) in enumerate(stats_data):
            card = QFrame()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 16, 18, 16)
            number = QLabel(value)
            number.setObjectName("sectionTitle")
            self._stat_values[key] = number
            description = QLabel(label)
            description.setObjectName("subtitle")
            description.setWordWrap(True)
            card_layout.addWidget(number)
            card_layout.addWidget(description)
            stats.addWidget(card, 0, column)

        quick = QLabel("Accesos rápidos")
        quick.setObjectName("sectionTitle")
        quick_actions = QGridLayout()
        quick_actions.setSpacing(12)
        destinations = (
            ("Resolver laboratorio", "Laboratorios"),
            ("Abrir juegos", "Juegos"),
            ("Convertir código", "Convertidor"),
            ("Consultar documentación", "Documentación"),
        )
        for index, (title_text, destination) in enumerate(destinations):
            button = QPushButton(title_text)
            button.setObjectName("secondaryButton")
            button.clicked.connect(lambda checked=False, target=destination: self._navigate(target))
            quick_actions.addWidget(button, index // 2, index % 2)

        self.refresh_stats()

        root.addWidget(hero)
        root.addLayout(stats)
        root.addWidget(quick)
        root.addLayout(quick_actions)
        root.addStretch()
