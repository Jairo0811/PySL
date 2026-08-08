import multiprocessing
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pysl.core.database import Database
from pysl.core.error_handler import configure_logging, install_global_exception_handler
from pysl.core.settings import SETTINGS
from pysl.ui.main_window import MainWindow
from pysl.ui.styles import DARK_THEME, DEFAULT_FONT_SIZE, apply_theme, normalize_theme


def _stored_font_size(database: Database) -> int:
    try:
        value = int(database.get_preference("font_size", str(DEFAULT_FONT_SIZE)))
    except ValueError:
        return DEFAULT_FONT_SIZE
    return max(11, min(24, value))


def main() -> int:
    multiprocessing.freeze_support()
    configure_logging()
    install_global_exception_handler()

    app = QApplication(sys.argv)
    app.setApplicationName(SETTINGS.app_name)
    app.setApplicationVersion(SETTINGS.version)
    app.setOrganizationName(SETTINGS.organization_name)
    app.setWindowIcon(QIcon(str(SETTINGS.assets_dir / "pysl-logo.ico")))

    database = Database()
    stored_theme = normalize_theme(database.get_preference("theme", DARK_THEME))
    apply_theme(app, stored_theme, _stored_font_size(database))

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
