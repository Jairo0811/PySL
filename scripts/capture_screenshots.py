from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Iterable
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QWidget

from pysl.modules.authentication.login_view import LoginView
from pysl.modules.authentication.service import AuthenticationService
from pysl.modules.dashboard.dashboard_view import DashboardView
from pysl.ui.styles import APP_STYLESHEET


def _render(widget: QWidget, destination: Path) -> None:
    widget.resize(1440, 900)
    widget.show()
    for _ in range(5):
        QApplication.processEvents()
    if not widget.grab().save(str(destination), "PNG"):
        raise RuntimeError(f"No se pudo crear la captura {destination}.")


def capture(output_directory: Path) -> Iterable[Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    login = LoginView(AuthenticationService(), lambda _username: None)
    login_path = output_directory / "login.png"
    _render(login, login_path)
    generated.append(login_path)
    login.close()

    dashboard = DashboardView("Jairo", lambda: None)
    for module_name, filename in (
        ("Inicio", "dashboard.png"),
        ("IDE de SL", "ide-sl.png"),
        ("Convertidor", "converter.png"),
    ):
        dashboard.navigate(module_name)
        path = output_directory / filename
        _render(dashboard, path)
        generated.append(path)
    dashboard.close()
    return generated


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera capturas reproducibles de PySL.")
    parser.add_argument("--output", type=Path, default=Path("assets/screenshots"))
    arguments = parser.parse_args()

    application = QApplication(sys.argv[:1])
    application.setStyleSheet(APP_STYLESHEET)
    for path in capture(arguments.output):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
