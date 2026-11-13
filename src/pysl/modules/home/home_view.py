from collections.abc import Callable

from PySide6.QtGui import QShowEvent
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

QUICK_ACCESS = (
    (
        "Laboratorio",
        "Resuelve el menor número par y compáralo con su algoritmo en SL.",
        "Resolver laboratorio",
        "Laboratorios",
    ),
    (
        "Arcade",
        "Ahorcado, adivina el número, piedra papel o tijera y tres en raya.",
        "Abrir juegos",
        "Juegos",
    ),
    (
        "Convertidor",
        "Traduce programas entre SL y Python y compara ambas sintaxis.",
        "Convertir código",
        "Convertidor",
    ),
    (
        "Documentación",
        "Referencia rápida de la sintaxis de SL, operadores y atajos del IDE.",
        "Consultar documentación",
        "Documentación",
    ),
)


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
        root.setSpacing(16)

        root.addWidget(self._build_hero())
        root.addLayout(self._build_stats())

        quick = QLabel("Accesos rápidos")
        quick.setObjectName("sectionTitle")
        root.addWidget(quick)
        root.addLayout(self._build_quick_access(), 1)

        self.refresh_stats()

    def _build_hero(self) -> QFrame:
        hero = QFrame()
        hero.setObjectName("card")
        layout = QVBoxLayout(hero)
        layout.setContentsMargins(32, 26, 32, 26)
        layout.setSpacing(8)

        eyebrow = QLabel("PLATAFORMA EDUCATIVA · SL + PYTHON")
        eyebrow.setObjectName("accent")
        title = QLabel(f"Bienvenido a PySL, {self._username}")
        title.setObjectName("pageTitle")
        body = QLabel(
            "Aprende programación estructurada con la claridad de SL y el poder de Python. "
            "Sigue el curso, practica en el IDE y compara tu código con su equivalente."
        )
        body.setObjectName("subtitle")
        body.setWordWrap(True)
        body.setMaximumWidth(760)

        actions = QHBoxLayout()
        actions.setSpacing(12)
        start = QPushButton("Comenzar en el IDE")
        start.clicked.connect(lambda: self._navigate("IDE de SL"))
        course = QPushButton("Continuar el curso")
        course.setObjectName("secondaryButton")
        course.clicked.connect(lambda: self._navigate("Curso"))
        actions.addWidget(start)
        actions.addWidget(course)
        actions.addStretch()

        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(body)
        layout.addSpacing(8)
        layout.addLayout(actions)
        return hero

    def _build_stats(self) -> QGridLayout:
        stats_data = (
            ("labs", "0", "Laboratorios completados"),
            ("played", "0", "Partidas jugadas"),
            ("won", "0", "Victorias"),
            ("version", SETTINGS.version, "Versión de PySL"),
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
            stats.setColumnStretch(column, 1)
        return stats

    def _build_quick_access(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(14)
        for index, (title_text, description_text, action_text, destination) in enumerate(
            QUICK_ACCESS
        ):
            card = QFrame()
            card.setObjectName("card")
            layout = QVBoxLayout(card)
            layout.setContentsMargins(20, 16, 20, 16)
            layout.setSpacing(6)
            heading = QLabel(title_text)
            heading.setObjectName("sectionTitle")
            description = QLabel(description_text)
            description.setObjectName("subtitle")
            description.setWordWrap(True)
            button = QPushButton(action_text)
            button.setObjectName("secondaryButton")
            button.clicked.connect(lambda checked=False, target=destination: self._navigate(target))
            layout.addWidget(heading)
            layout.addWidget(description)
            layout.addStretch()
            layout.addWidget(button)
            grid.addWidget(card, index // 2, index % 2)
            grid.setColumnStretch(index % 2, 1)
            grid.setRowStretch(index // 2, 1)
        return grid
