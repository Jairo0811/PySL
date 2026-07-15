from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QStackedWidget

from pysl.core.session import UserSession
from pysl.core.settings import SETTINGS
from pysl.modules.authentication.login_view import LoginView
from pysl.modules.authentication.service import AuthenticationService
from pysl.modules.dashboard.dashboard_view import DashboardView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._session = UserSession()
        self._authentication_service = AuthenticationService()
        self._stack = QStackedWidget()
        self.setWindowTitle(f"{SETTINGS.app_name} {SETTINGS.version}")
        self.setWindowIcon(QIcon(str(SETTINGS.assets_dir / "pysl-logo.ico")))
        self.resize(SETTINGS.window_width, SETTINGS.window_height)
        self.setMinimumSize(1100, 700)
        self.setCentralWidget(self._stack)
        self._show_login()

    def _show_login(self) -> None:
        self._replace_current_view(LoginView(self._authentication_service, self._handle_authenticated))

    def _handle_authenticated(self, username: str) -> None:
        self._session.start(username)
        self._replace_current_view(DashboardView(username, self._handle_logout))

    def _handle_logout(self) -> None:
        self._session.clear(); self._show_login()

    def _replace_current_view(self, widget) -> None:  # type: ignore[no-untyped-def]
        while self._stack.count():
            current = self._stack.widget(0); self._stack.removeWidget(current); current.deleteLater()
        self._stack.addWidget(widget); self._stack.setCurrentWidget(widget)
