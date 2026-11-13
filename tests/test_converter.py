import pytest

from pysl.modules.converter.service import CodeConverter, ConversionError


def test_converts_sl_to_standard_python() -> None:
    converted = CodeConverter().sl_to_python('inicio\nimprimir("Hola")\nfin')
    assert 'print("Hola")' in converted
    assert "__imprimir__" not in converted


def test_converts_sl_input_to_standard_python() -> None:
    converted = CodeConverter().sl_to_python("inicio\nleer(nombre)\nfin")
    assert "nombre = input()" in converted
    assert "__leer__" not in converted


def test_converts_basic_python_to_sl() -> None:
    converted = CodeConverter().python_to_sl('nombre = input("Nombre: ")\nprint(nombre)')
    assert "leer(nombre)" in converted
    assert "imprimir(nombre)" in converted


def test_converts_nested_python_blocks_and_else() -> None:
    converted = CodeConverter().python_to_sl(
        """for numero in range(1, 4):
    if numero % 2 == 0:
        print("par", numero)
    else:
        print("impar", numero)
"""
    )

    assert "para numero desde 1 hasta 3" in converted
    assert "sino" in converted
    assert converted.count("finsi") == 1
    assert converted.count("finpara") == 1


def test_python_to_sl_rejects_unsupported_imports() -> None:
    with pytest.raises(ConversionError, match="Import"):
        CodeConverter().python_to_sl("import os")


def test_python_to_sl_preserves_words_inside_strings() -> None:
    converted = CodeConverter().python_to_sl('print("True and False")')

    assert "True and False" in converted
    assert "verdadero" not in converted
    assert "falso" not in converted


@pytest.mark.parametrize(
    ("python_range", "expected"),
    [
        ("range(5)", "para i desde 0 hasta 4"),
        ("range(2, 7)", "para i desde 2 hasta 6"),
        ("range(n)", "para i desde 0 hasta n - 1"),
        ("range(1, n + 1)", "para i desde 1 hasta n"),
        ("range(1, len(v))", "para i desde 1 hasta (len(v)) - 1"),
    ],
)
def test_range_bounds_are_converted_to_readable_inclusive_limits(
    python_range: str, expected: str
) -> None:
    converted = CodeConverter().python_to_sl(f"for i in {python_range}:\n    print(i)\n")

    assert expected in converted


def test_converted_range_loop_runs_the_same_iterations() -> None:
    from pysl.language import SLExecutor

    python_source = "for i in range(1, 4):\n    print(i)\n"
    sl_source = CodeConverter().python_to_sl(python_source)

    assert SLExecutor().execute(sl_source).output == "1\n2\n3"
