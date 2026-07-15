from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from pysl.core.settings import SETTINGS


class GalleryView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        title = QLabel("Galería histórica")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Recursos recuperados del proyecto web original, conservados como memoria académica.")
        subtitle.setObjectName("subtitle")
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        content = QWidget(); grid = QGridLayout(content); grid.setSpacing(14)
        images = sorted([p for p in SETTINGS.legacy_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])[:12]
        for index, path in enumerate(images):
            image = QLabel(); image.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image.setMinimumSize(260, 220)
            pixmap = QPixmap(str(path))
            image.setPixmap(pixmap.scaled(250, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            image.setToolTip(path.name)
            grid.addWidget(image, index // 4, index % 4)
        scroll.setWidget(content)
        root.addWidget(title); root.addWidget(subtitle); root.addWidget(scroll, 1)
