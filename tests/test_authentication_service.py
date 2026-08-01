from pysl.modules.authentication.service import AuthenticationService


def test_authentication_accepts_explicit_guest_access() -> None:
    service = AuthenticationService()

    result = service.authenticate_demo()

    assert result.is_valid is True


def test_authentication_rejects_invalid_password() -> None:
    service = AuthenticationService()

    result = service.authenticate("Jairo", "incorrecta")

    assert result.is_valid is False
