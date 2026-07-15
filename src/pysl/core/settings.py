from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _resource_root() -> Path:
    """Return the bundled resource directory in development and PyInstaller builds."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[3]


def _user_data_root(app_name: str) -> Path:
    """Return a writable per-user directory for databases and preferences."""
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / app_name


@dataclass(frozen=True, slots=True)
class AppSettings:
    app_name: str = "PySL"
    organization_name: str = "Francis Jairo Matías Rosario"
    version: str = "1.0.2"
    window_width: int = 1440
    window_height: int = 900

    @property
    def project_root(self) -> Path:
        return _resource_root()

    @property
    def assets_dir(self) -> Path:
        return self.project_root / "assets"

    @property
    def bundled_data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def data_dir(self) -> Path:
        path = _user_data_root(self.app_name)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def legacy_dir(self) -> Path:
        return self.project_root / "legacy" / "web-original"


SETTINGS = AppSettings()
