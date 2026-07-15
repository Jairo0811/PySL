import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pysl.core.settings import SETTINGS
from pysl.ui.main_window import MainWindow
from pysl.ui.styles import APP_STYLESHEET


def main() -> int:
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
