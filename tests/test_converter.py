import pytest

from pysl.modules.converter.service import CodeConverter, ConversionError


def test_converts_sl_to_python() -> None:
    converted = CodeConverter().sl_to_python('inicio\nimprimir("Hola")\nfin')
    assert '__imprimir__("Hola")' in converted


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

    assert "para numero desde 1 hasta (4) - 1" in converted
    assert "sino" in converted
    assert converted.count("finsi") == 1
    assert converted.count("finpara") == 1


def test_python_to_sl_rejects_unsupported_imports() -> None:
    with pytest.raises(ConversionError, match="Import"):
        CodeConverter().python_to_sl("import os")


def test_python_to_sl_preserves_words_inside_strings() -> None:
    converted = CodeConverter().python_to_sl('print("True and False")')

    assert 'imprimir("True and False")' in converted
