import multiprocessing
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pysl.core.error_handler import configure_logging, install_global_exception_handler
from pysl.core.settings import SETTINGS
from pysl.ui.main_window import MainWindow
from pysl.ui.styles import APP_STYLESHEET


def main() -> int:
    multiprocessing.freeze_support()
    configure_logging()
    install_global_exception_handler()
    app = QApplication(sys.argv)
    app.setApplicationName(SETTINGS.app_name)
    app.setApplicationVersion(SETTINGS.version)
    app.setOrganizationName(SETTINGS.organization_name)
    app.setWindowIcon(QIcon(str(SETTINGS.assets_dir / "pysl-logo.ico")))
    app.setStyleSheet(APP_STYLESHEET)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
