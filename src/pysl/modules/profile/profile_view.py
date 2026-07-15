import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from pysl.core.settings import SETTINGS


class ProfileView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._build_ui()

    def _build_ui(self) -> None:
        data = json.loads((SETTINGS.bundled_data_dir / "profile.json").read_text(encoding="utf-8"))
        root = QVBoxLayout(self)
        title = QLabel("Mi perfil")
        title.setObjectName("pageTitle")
        subtitle = QLabel("La evolución académica detrás de PySL.")
        subtitle.setObjectName("subtitle")
        card = QFrame(); card.setObjectName("card")
        layout = QHBoxLayout(card)
        photo = QLabel()
        image_path = SETTINGS.legacy_dir / "1.jpg"
        pixmap = QPixmap(str(image_path))
        photo.setPixmap(pixmap.scaled(240, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        details = QVBoxLayout()
        name = QLabel(data.get("full_name", "Francis Jairo Matías Rosario")); name.setObjectName("sectionTitle")
        details.addWidget(name)
        for label, key in (("Proyecto", "project"), ("Institución", "institution"), ("Materia original", "course"), ("Nacionalidad", "nationality")):
            value = data.get(key, "")
            row = QLabel(f"<b>{label}:</b> {value}")
            row.setWordWrap(True)
            details.addWidget(row)
        bio = QLabel("PySL recupera un proyecto final de Fundamentos de Programación (SOF-001) y lo transforma en una plataforma educativa moderna, modular y mantenible.")
        bio.setObjectName("subtitle"); bio.setWordWrap(True)
        details.addSpacing(12); details.addWidget(bio); details.addStretch()
        layout.addWidget(photo); layout.addLayout(details, 1)
        root.addWidget(title); root.addWidget(subtitle); root.addWidget(card); root.addStretch()
