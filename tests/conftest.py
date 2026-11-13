from __future__ import annotations

import gc
import os
from collections.abc import Iterator

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication

_APPLICATION: QApplication | None = None


@pytest.fixture(scope="session")
def qapp() -> Iterator[QApplication]:
    """Single QApplication, torn down in a controlled order.

    Destroying widgets *after* the application at interpreter exit segfaults on some
    Linux runners even though every test passed, so widgets are released first.
    """
    global _APPLICATION
    _APPLICATION = QApplication.instance() or QApplication([])  # type: ignore[assignment]
    yield _APPLICATION
    QThreadPool.globalInstance().waitForDone(5000)
    for widget in _APPLICATION.topLevelWidgets():
        widget.deleteLater()
    _APPLICATION.setStyleSheet("")
    _APPLICATION.processEvents()
    gc.collect()
    _APPLICATION.processEvents()
