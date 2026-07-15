from pysl.modules.authentication.service import AuthenticationService


def test_authentication_accepts_demo_credentials() -> None:
    service = AuthenticationService()

    result = service.authenticate("Jairo", "pysl2026")

    assert result.is_valid is True


def test_authentication_rejects_invalid_password() -> None:
    service = AuthenticationService()

    result = service.authenticate("Jairo", "incorrecta")

    assert result.is_valid is False
