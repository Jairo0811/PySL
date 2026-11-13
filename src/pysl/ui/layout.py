from __future__ import annotations

from PySide6.QtWidgets import QFrame, QScrollArea, QWidget


def scrollable(page: QWidget) -> QScrollArea:
    """Wrap ``page`` so it scrolls instead of squeezing its controls in small windows."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setFrameShape(QFrame.Shape.NoFrame)
    area.setWidget(page)
    return area
