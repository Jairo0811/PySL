from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pysl.modules.authentication.service import AuthenticationService


class LoginView(QWidget):
    def __init__(
        self,
        authentication_service: AuthenticationService,
        on_authenticated: Callable[[str], None],
    ) -> None:
        super().__init__()
        self._authentication_service = authentication_service
        self._on_authenticated = on_authenticated
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(430)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(34, 34, 34, 34)
        card_layout.setSpacing(16)

        title = QLabel("PySL")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Fundamentos de Programación Reimagined")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._username_input = QLineEdit()
        self._username_input.setPlaceholderText("Usuario")
        self._username_input.setText("Jairo")

        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Contraseña")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_input.returnPressed.connect(self._authenticate)

        self._message_label = QLabel("")
        self._message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._message_label.setWordWrap(True)

        login_button = QPushButton("Iniciar sesión")
        login_button.clicked.connect(self._authenticate)

        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(8)
        card_layout.addWidget(self._username_input)
        card_layout.addWidget(self._password_input)
        card_layout.addWidget(self._message_label)
        card_layout.addWidget(login_button)

        root.addWidget(card)

    def _authenticate(self) -> None:
        result = self._authentication_service.authenticate(
            self._username_input.text(),
            self._password_input.text(),
        )

        if not result.is_valid:
            self._message_label.setText(f"☹ {result.message}")
            return

        self._message_label.clear()
        self._on_authenticated(self._username_input.text().strip())
