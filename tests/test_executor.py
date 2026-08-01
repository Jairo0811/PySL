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
