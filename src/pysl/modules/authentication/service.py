from dataclasses import dataclass
from hmac import compare_digest


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    is_valid: bool
    message: str


class AuthenticationService:
    """Validación local temporal para el MVP de PySL."""

    _demo_username = "Jairo"
    _demo_password = "pysl2026"

    def authenticate(self, username: str, password: str) -> AuthenticationResult:
        normalized_username = username.strip()

        if not normalized_username or not password:
            return AuthenticationResult(False, "Completa el usuario y la contraseña.")

        valid_username = compare_digest(normalized_username.casefold(), self._demo_username.casefold())
        valid_password = compare_digest(password, self._demo_password)

        if not (valid_username and valid_password):
            return AuthenticationResult(False, "Usuario o contraseña incorrectos.")

        return AuthenticationResult(True, "Acceso concedido.")
