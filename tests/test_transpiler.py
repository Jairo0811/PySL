import pytest
from pysl.language.transpiler import PySLTranspiler, TranspilationError


def test_transpiles_basic_program() -> None:
    code = """inicio
leer(numero)
si numero % 2 == 0 entonces
imprimir("par")
sino
imprimir("impar")
finsi
fin"""
    result = PySLTranspiler().transpile(code).python_code
    assert "numero = __leer__()" in result
    assert "if numero % 2 == 0:" in result
    assert "else:" in result


def test_requires_start_and_end() -> None:
    with pytest.raises(TranspilationError):
        PySLTranspiler().transpile('imprimir("hola")')
