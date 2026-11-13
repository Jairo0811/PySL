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


def test_empty_imprimir_prints_a_blank_line() -> None:
    result = SLTranspiler().transpile("inicio\nimprimir()\nfin")

    assert "__imprimir__()" in result.python_code


@pytest.mark.parametrize(
    "source",
    [
        "inicio\nclass = 3\nfin",
        "inicio\nleer(import)\nfin",
        "inicio\npara None desde 1 hasta 2\nimprimir(1)\nfinpara\nfin",
        "funcion lambda(a)\nretornar a\nfinfuncion\ninicio\nfin",
        "funcion f(def)\nretornar 1\nfinfuncion\ninicio\nfin",
    ],
)
def test_rejects_python_reserved_words_as_names(source: str) -> None:
    with pytest.raises(TranspilationError, match="palabra reservada") as error:
        SLTranspiler().transpile(source)

    assert error.value.line is not None


def test_maps_generated_python_lines_back_to_sl_lines() -> None:
    program = SLTranspiler().transpile(
        "\n".join(
            [
                "// comentario",  # 1
                "inicio",  # 2
                "si verdadero entonces",  # 3
                "    imprimir(1)",  # 4
                "sino",  # 5
                "    imprimir(2)",  # 6
                "finsi",  # 7
                "fin",  # 8
            ]
        )
    )

    assert program.python_code.splitlines()[0] == "if True:"
    assert program.line_map == (3, 4, 5, 6)
    assert program.sl_line(1) == 3
    assert program.sl_line(3) == 5
    assert program.sl_line(99) is None
    assert program.sl_line(None) is None


def test_transpilation_errors_expose_their_line() -> None:
    with pytest.raises(TranspilationError) as error:
        SLTranspiler().transpile("inicio\nimprimir(1)\nfinsi\nfin")

    assert error.value.line == 3


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("// comentario", 0),
        ("    // comentario", 4),
        ("# comentario", 0),
        ("x = 5 # nota", 6),
        ("x = 5 // 2", None),  # integer division, not a comment
        ('imprimir("http://ejemplo.com")', None),
        ('imprimir("a # b")', None),
        ('imprimir("a # b") # real', 18),
        ("imprimir('it # works')", None),
        ('imprimir("comilla \\" # sigue en cadena")', None),
        ("entero x = 1", None),
    ],
)
def test_comment_start_distinguishes_comments_from_division_and_strings(
    line: str, expected: int | None
) -> None:
    assert SLTranspiler.comment_start(line) == expected


@pytest.mark.parametrize(
    "statement",
    [
        "imprimir(1) # nota",
        "leer(dato) # nota",
        "valor = 2 # nota",
        "entero valor # nota",
        "fin # nota",
    ],
)
def test_inline_hash_comments_are_accepted_after_any_statement(statement: str) -> None:
    body = statement if statement != "fin # nota" else "imprimir(1)"
    ending = "fin # nota" if statement == "fin # nota" else "fin"
    program = f"inicio # arranque\n{body}\n{ending}"

    SLTranspiler().transpile(program)


def test_inline_comments_work_on_block_keywords() -> None:
    source = (
        "funcion doble(n) # parámetro\n"
        "    retornar n * 2 # resultado\n"
        "finfuncion # fin de la función\n"
        "inicio\n"
        "    si verdadero entonces # siempre\n"
        "        imprimir(doble(2)) # 4\n"
        "    sino # nunca\n"
        "        imprimir(0)\n"
        "    finsi # listo\n"
        "fin\n"
    )

    program = SLTranspiler().transpile(source)

    assert "def doble(n):" in program.python_code
    assert "else:" in program.python_code


def test_hash_inside_strings_is_not_a_comment_and_floor_division_survives() -> None:
    result = SLTranspiler().transpile('inicio\nimprimir("a # b", 7 // 2) # real\nfin')

    assert '__imprimir__("a # b", 7 // 2)' in result.python_code
