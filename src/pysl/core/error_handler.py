from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType

from PySide6.QtWidgets import QApplication, QMessageBox

from pysl.core.settings import SETTINGS

LOGGER = logging.getLogger("pysl")


def configure_logging() -> Path:
    """Configure a bounded per-user log and return its path."""
    log_directory = SETTINGS.data_dir / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / "pysl.log"

    if not LOGGER.handlers:
        handler = RotatingFileHandler(
            log_path,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        )
        LOGGER.addHandler(handler)
        LOGGER.setLevel(logging.INFO)
        LOGGER.propagate = False
    return log_path


def install_global_exception_handler() -> None:
    """Log uncaught UI errors and show a concise recovery message."""
    previous_hook = sys.excepthook

    def handle_exception(
        exception_type: type[BaseException],
        exception: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        if issubclass(exception_type, KeyboardInterrupt):
            previous_hook(exception_type, exception, traceback)
            return
        LOGGER.critical(
            "Unhandled application error",
            exc_info=(exception_type, exception, traceback),
        )
        if QApplication.instance() is not None:
            QMessageBox.critical(
                None,
                "Error inesperado",
                "PySL encontró un error inesperado. Los detalles se guardaron en el "
                "registro local. Puedes reiniciar la aplicación de forma segura.",
            )

    sys.excepthook = handle_exception
