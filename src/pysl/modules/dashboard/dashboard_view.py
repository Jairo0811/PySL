from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from pysl.core.settings import SETTINGS
from pysl.modules.about.about_view import AboutView
from pysl.modules.converter.converter_view import ConverterView
from pysl.modules.course.course_view import CourseView
from pysl.modules.docs.docs_view import DocsView
from pysl.modules.editor.editor_view import EditorView
from pysl.modules.exercises.smallest_even.view import SmallestEvenView
from pysl.modules.gallery.gallery_view import GalleryView
from pysl.modules.games.games_view import GamesView
from pysl.modules.home.home_view import HomeView
from pysl.modules.profile.profile_view import ProfileView
from pysl.modules.settings.settings_view import SettingsView


class DashboardView(QWidget):
    MODULES = (
        "Inicio",
        "Mi perfil",
        "Curso",
        "Laboratorios",
        "Juegos",
        "IDE PySL",
        "Convertidor",
        "Galería",
        "Documentación",
        "Configuración",
        "Acerca de PySL",
    )

    def __init__(self, username: str, on_logout: Callable[[], None]) -> None:
        super().__init__()
        self._username = username
        self._on_logout = on_logout
        self._index_by_name: dict[str, int] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(18)

        sidebar_frame = QFrame()
        sidebar_frame.setObjectName("sidebar")
        sidebar_frame.setFixedWidth(270)
        sidebar = QVBoxLayout(sidebar_frame)
        sidebar.setContentsMargins(14, 14, 14, 14)
        sidebar.setSpacing(8)

        logo = QLabel()
        pixmap = QPixmap(str(SETTINGS.assets_dir / "pysl-logo.png"))
        if not pixmap.isNull():
            logo.setPixmap(
                pixmap.scaled(
                    128,
                    128,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setMinimumHeight(132)

        user = QLabel(f"Sesión: {self._username}")
        user.setObjectName("subtitle")
        user.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._menu = QListWidget()
        self._menu.setObjectName("mainMenu")
        icons = ("⌂", "♙", "▤", "⚗", "▣", "</>", "⇄", "▧", "?", "⚙", "ⓘ")
        for icon, title in zip(icons, self.MODULES, strict=True):
            self._menu.addItem(QListWidgetItem(f"{icon}   {title}"))
        self._menu.currentRowChanged.connect(self._pages_set_current_index)

        logout = QPushButton("Cerrar sesión")
        logout.setObjectName("dangerButton")
        logout.clicked.connect(self._on_logout)

        sidebar.addWidget(logo)
        sidebar.addWidget(user)
        sidebar.addSpacing(8)
        sidebar.addWidget(self._menu, 1)
        sidebar.addWidget(logout)

        self._pages = QStackedWidget()
        pages = [
            HomeView(self._username, self.navigate),
            ProfileView(),
            CourseView(),
            SmallestEvenView(),
            GamesView(),
            EditorView(),
            ConverterView(),
            GalleryView(),
            DocsView(),
            SettingsView(),
            AboutView(),
        ]
        for index, (name, page) in enumerate(zip(self.MODULES, pages, strict=True)):
            self._index_by_name[name] = index
            self._pages.addWidget(page)

        root.addWidget(sidebar_frame)
        root.addWidget(self._pages, 1)
        self._menu.setCurrentRow(0)

    def navigate(self, module_name: str) -> None:
        aliases = {
            "Laboratorio": "Laboratorios",
            "Editor PySL": "IDE PySL",
            "Acerca de": "Acerca de PySL",
        }
        index = self._index_by_name.get(aliases.get(module_name, module_name))
        if index is not None:
            self._menu.setCurrentRow(index)

    def _pages_set_current_index(self, index: int) -> None:
        if index >= 0:
            self._pages.setCurrentIndex(index)
