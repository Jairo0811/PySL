from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class AboutView(QWidget):
    """Presentación institucional y académica de PySL."""

    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("aboutView")
        self._build_ui()

    def _build_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        content = QWidget()
        content.setObjectName("aboutContent")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(48, 45, 48, 45)
        content_layout.setSpacing(14)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        content_layout.addWidget(self._create_itla_logo())
        content_layout.addSpacing(6)

        title = QLabel("PySL")
        title.setObjectName("aboutTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(title)

        version = QLabel("Versión 1.0.2")
        version.setObjectName("aboutVersion")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(version)

        slogan = QLabel("Python + SL = Aprender, Crear, Programar")
        slogan.setObjectName("aboutSlogan")
        slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(slogan)

        content_layout.addSpacing(4)
        content_layout.addWidget(self._create_separator())
        content_layout.addSpacing(8)

        institution = QLabel(
            "Instituto Tecnológico de Las Américas\n"
            "(ITLA)"
        )
        institution.setObjectName("aboutInstitution")
        institution.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(institution)

        content_layout.addSpacing(12)

        content_layout.addWidget(
            self._create_academic_field(
                "Autor",
                "Francis Jairo Matías Rosario",
            )
        )

        content_layout.addWidget(
            self._create_academic_field(
                "Matrícula",
                "2015-2984",
            )
        )

        content_layout.addWidget(
            self._create_academic_field(
                "Materia",
                "Fundamentos de Programación (SOF-001)",
            )
        )

        content_layout.addWidget(
            self._create_academic_field(
                "Período académico",
                "2016-C2",
            )
        )

        content_layout.addWidget(
            self._create_academic_field(
                "Profesor",
                "Freidy Ramón Núñez Pérez",
            )
        )

        content_layout.addStretch()

        scroll_area.setWidget(content)
        root_layout.addWidget(scroll_area)

    def _create_itla_logo(self) -> QLabel:
        """Carga y muestra el logo institucional del ITLA."""

        logo_label = QLabel()
        logo_label.setObjectName("itlaLogo")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_label.setMinimumSize(360, 150)
        logo_label.setMaximumHeight(170)
        logo_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        logo_path = self._resolve_itla_logo_path()
        pixmap = QPixmap(str(logo_path))

        if pixmap.isNull():
            logo_label.setText("ITLA")
            logo_label.setObjectName("itlaLogoFallback")
            return logo_label

        scaled_pixmap = pixmap.scaled(
            310,
            140,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        logo_label.setPixmap(scaled_pixmap)

        return logo_label

    @staticmethod
    def _resolve_itla_logo_path() -> Path:
        """
        Resuelve la ruta del logo tanto en desarrollo como
        dentro del ejecutable generado con PyInstaller.
        """

        relative_path = Path(
            "assets",
            "ITLA-logo-fondo-blanco.png",
        )

        try:
            from pysl.core.paths import resource_path

            bundled_path = Path(
                resource_path(relative_path.as_posix())
            )

            if bundled_path.exists():
                return bundled_path
        except (ImportError, TypeError, AttributeError):
            pass

        project_root = Path(__file__).resolve().parents[4]

        return project_root / relative_path

    @staticmethod
    def _create_separator() -> QFrame:
        """Crea un separador horizontal centralizado."""

        separator = QFrame()
        separator.setObjectName("aboutSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setMaximumWidth(560)

        return separator

    @staticmethod
    def _create_academic_field(
        label_text: str,
        value_text: str,
    ) -> QWidget:
        """Crea un campo académico con etiqueta y valor."""

        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 2, 0, 9)
        layout.setSpacing(4)

        label = QLabel(label_text)
        label.setObjectName("academicFieldLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value = QLabel(value_text)
        value.setObjectName("academicFieldValue")
        value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value.setWordWrap(True)

        layout.addWidget(label)
        layout.addWidget(value)

        return container