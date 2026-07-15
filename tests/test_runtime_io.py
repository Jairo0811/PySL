from pysl.runtime.io import leer_entero


def test_leer_entero_retries_after_invalid_input() -> None:
    answers = iter(["texto", "42"])
    errors: list[str] = []

    result = leer_entero(input_fn=lambda _: next(answers), error_fn=errors.append)

    assert result == 42
    assert errors == ["Entrada inválida. Digite un número entero."]
