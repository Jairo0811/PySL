import pytest

from pysl.language.executor import ExecutionLimitExceeded, ExecutionLimits, SLExecutor


def test_executes_input_loop_and_output() -> None:
    code = """inicio
leer(numero)
para i desde 1 hasta 3
imprimir(numero * i)
finpara
fin"""
    result = SLExecutor().execute(code, ["4"])
    assert result.output == "4\n8\n12"
    assert result.variables["numero"] == 4


def test_stops_an_infinite_loop_by_step_limit() -> None:
    executor = SLExecutor(limits=ExecutionLimits(max_steps=1_000, timeout_seconds=5.0))
    source = """inicio
mientras verdadero
    entero valor = 1
finmientras
fin"""

    with pytest.raises(ExecutionLimitExceeded, match="pasos"):
        executor.execute(source)


def test_limits_output_lines() -> None:
    executor = SLExecutor(limits=ExecutionLimits(max_output_lines=3))
    source = """inicio
para i desde 1 hasta 4
    imprimir(i)
finpara
fin"""

    with pytest.raises(ExecutionLimitExceeded, match="salida"):
        executor.execute(source)


def test_rejects_reserved_runtime_names() -> None:
    source = """inicio
int = 3
fin"""

    with pytest.raises(RuntimeError, match="reservado"):
        SLExecutor().execute(source)


@pytest.mark.parametrize(
    ("body", "expected_message"),
    [
        ("x = 1 / 0", "división entre cero"),
        ("vector v = [1, 2]\nimprimir(v[5])", "fuera del rango"),
        ("imprimir(desconocida)", "'desconocida' no está definida"),
        ('x = "a" + 1', "tipos de datos no son compatibles"),
        ('x = int("abc")', "no se pudo convertir"),
        ("numerico x\nimprimir(x + 1)", "todavía no tiene valor"),
    ],
)
def test_runtime_errors_are_spanish(body: str, expected_message: str) -> None:
    with pytest.raises(RuntimeError, match=expected_message) as error:
        SLExecutor().execute(f"inicio\n{body}\nfin")

    message = str(error.value)
    assert message.startswith("Error de ejecución:")
    assert "division by zero" not in message
    assert "is not defined" not in message


def test_runtime_errors_report_the_sl_line() -> None:
    source = "// comentario\ninicio\nimprimir(1)\nx = 1 / 0\nfin"

    with pytest.raises(RuntimeError, match=r"\(línea 4\)") as error:
        SLExecutor().execute(source)

    assert error.value.line == 4  # type: ignore[attr-defined]


def test_limit_errors_report_the_sl_line() -> None:
    executor = SLExecutor(limits=ExecutionLimits(max_steps=500, timeout_seconds=5.0))
    source = "inicio\nentero n = 0\nmientras verdadero\n    n = n + 1\nfinmientras\nfin"

    with pytest.raises(ExecutionLimitExceeded, match="línea") as error:
        executor.execute(source)

    assert error.value.line in {3, 4}


def test_errors_inside_functions_point_to_the_function_body() -> None:
    source = "funcion dividir(a, b)\n    retornar a / b\nfinfuncion\ninicio\nimprimir(dividir(1, 0))\nfin"

    with pytest.raises(RuntimeError, match=r"\(línea 2\)"):
        SLExecutor().execute(source)


def test_wrong_argument_count_has_a_clear_message() -> None:
    source = "funcion f(a)\n    retornar a\nfinfuncion\ninicio\nimprimir(f(1, 2))\nfin"

    with pytest.raises(RuntimeError, match="cantidad de argumentos"):
        SLExecutor().execute(source)


def test_empty_imprimir_produces_a_blank_output_line() -> None:
    result = SLExecutor().execute('inicio\nimprimir("a")\nimprimir()\nimprimir("b")\nfin')

    assert result.output == "a\n\nb"


def test_programs_with_inline_comments_execute() -> None:
    source = """// Programa con comentarios
inicio # arranque
    entero a = 7 # valor
    si a // 2 == 3 entonces # división entera, no comentario
        imprimir("ok # no soy comentario") # salida
    finsi # fin
fin # listo
"""

    assert SLExecutor().execute(source).output == "ok # no soy comentario"


@pytest.mark.parametrize(
    "expression",
    ['"%900000000d" % 1', '"%s" % "a"', '"%s%s" % [1, 2]', "[1, 2] % 2"],
)
def test_percent_operator_rejects_text_formatting_before_allocating(expression: str) -> None:
    with pytest.raises(RuntimeError, match="solo admite números"):
        SLExecutor().execute(f"inicio\nx = {expression}\nfin")


def test_percent_operator_still_works_for_numbers() -> None:
    assert (
        SLExecutor().execute("inicio\nimprimir(17 % 5, -7 % 3, 7.5 % 2)\nfin").output == "2 2 1.5"
    )
