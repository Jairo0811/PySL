import hashlib
from dataclasses import dataclass
from hmac import compare_digest


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    is_valid: bool
    message: str


class AuthenticationService:
    """Validate the local demonstration account without storing its plain password."""

    _demo_username = "Jairo"
    _credential_salt = b"PySL-demo-account-v1"
    _credential_digest = bytes.fromhex(
        "73dbb9cbea5ebfff720bca41d0ddcd251ca36fb3171864fe65ef0b76606c2943"
    )
    _iterations = 240_000

    def authenticate(self, username: str, password: str) -> AuthenticationResult:
        normalized_username = username.strip()

        if not normalized_username or not password:
            return AuthenticationResult(False, "Completa el usuario y la contraseña.")

        valid_username = compare_digest(
            normalized_username.casefold(), self._demo_username.casefold()
        )
        candidate_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            self._credential_salt,
            self._iterations,
        )
        valid_password = compare_digest(candidate_digest, self._credential_digest)

        if not (valid_username and valid_password):
            return AuthenticationResult(False, "Usuario o contraseña incorrectos.")

        return AuthenticationResult(True, "Acceso concedido.")

    def authenticate_demo(self, username: str = "Invitado") -> AuthenticationResult:
        """Open an explicit local guest session without treating it as an identity."""
        if not username.strip():
            return AuthenticationResult(False, "El nombre de la sesión no es válido.")
        return AuthenticationResult(True, "Acceso de demostración concedido.")
