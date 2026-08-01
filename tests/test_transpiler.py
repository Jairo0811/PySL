import pytest

from pysl.language.transpiler import SLTranspiler, TranspilationError


def test_transpiles_basic_program() -> None:
    code = """inicio
leer(numero)
si numero % 2 == 0 entonces
imprimir("par")
sino
imprimir("impar")
finsi
fin"""
    result = SLTranspiler().transpile(code).python_code
    assert "numero = __leer__()" in result
    assert "if numero % 2 == 0:" in result
    assert "else:" in result


def test_requires_start_and_end() -> None:
    with pytest.raises(TranspilationError):
        SLTranspiler().transpile('imprimir("hola")')


def test_preserves_logical_words_inside_strings() -> None:
    result = SLTranspiler().transpile('inicio\nimprimir("verdadero y falso")\nfin')

    assert '"verdadero y falso"' in result.python_code


def test_rejects_statement_injection_inside_an_expression() -> None:
    with pytest.raises(TranspilationError, match="Expresión inválida"):
        SLTranspiler().transpile("inicio\nvalor = 1; imprimir(2)\nfin")


def test_rejects_instructions_after_end() -> None:
    with pytest.raises(TranspilationError, match="después de 'fin'"):
        SLTranspiler().transpile("inicio\nfin\nimprimir(1)")


def test_rejects_empty_blocks() -> None:
    with pytest.raises(TranspilationError, match="está vacío"):
        SLTranspiler().transpile("inicio\nsi verdadero\nfinsi\nfin")
