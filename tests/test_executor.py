from pysl.language.executor import PySLExecutor


def test_executes_input_loop_and_output() -> None:
    code = """inicio
leer(numero)
para i desde 1 hasta 3
imprimir(numero * i)
finpara
fin"""
    result = PySLExecutor().execute(code, ["4"])
    assert result.output == "4\n8\n12"
    assert result.variables["numero"] == 4
