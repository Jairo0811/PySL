from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any

from pysl.language.transpiler import PySLTranspiler


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    output: str
    python_code: str
    variables: dict[str, Any]


class PySLExecutor:
    """Execute transpiled PySL inside a restricted Python environment."""

    _ALLOWED_NODES = (
        ast.Module, ast.Assign, ast.Name, ast.Load, ast.Store, ast.Constant,
        ast.Expr, ast.Call, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
        ast.If, ast.While, ast.For, ast.FunctionDef, ast.Return, ast.arguments,
        ast.arg, ast.List, ast.Tuple, ast.Subscript, ast.Slice,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
        ast.USub, ast.UAdd, ast.And, ast.Or, ast.Not, ast.Eq, ast.NotEq,
        ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    )

    def __init__(self, transpiler: PySLTranspiler | None = None) -> None:
        self._transpiler = transpiler or PySLTranspiler()

    def execute(self, source: str, inputs: list[str] | None = None) -> ExecutionResult:
        program = self._transpiler.transpile(source)
        tree = ast.parse(program.python_code, mode="exec")
        self._validate(tree)
        pending_inputs = iter(inputs or [])
        output_lines: list[str] = []

        def read_value() -> object:
            try:
                return self._coerce(next(pending_inputs))
            except StopIteration as exc:
                raise RuntimeError("El programa solicitó más entradas de las proporcionadas.") from exc

        def print_value(*values: object) -> None:
            output_lines.append(" ".join(str(value) for value in values))

        environment: dict[str, Any] = {
            "__builtins__": {}, "__leer__": read_value, "__imprimir__": print_value,
            "int": int, "float": float, "str": str, "range": range, "len": len,
            "min": min, "max": max, "sum": sum,
        }
        exec(compile(tree, "<pysl>", "exec"), environment, environment)
        excluded = {"int", "float", "str", "range", "len", "min", "max", "sum"}
        variables = {k: v for k, v in environment.items() if not k.startswith("__") and k not in excluded and not callable(v)}
        return ExecutionResult("\n".join(output_lines), program.python_code, variables)

    def _validate(self, tree: ast.AST) -> None:
        allowed_calls = {"__leer__", "__imprimir__", "int", "float", "str", "range", "len", "min", "max", "sum"}
        declared_functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        for node in ast.walk(tree):
            if not isinstance(node, self._ALLOWED_NODES):
                raise RuntimeError(f"Construcción no permitida en PySL: {type(node).__name__}")
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in allowed_calls | declared_functions:
                    raise RuntimeError("La llamada solicitada no está permitida.")

    @staticmethod
    def _coerce(raw: str) -> object:
        value = raw.strip()
        if value.lower() in {"verdadero", "true"}: return True
        if value.lower() in {"falso", "false"}: return False
        try: return int(value)
        except ValueError:
            try: return float(value)
            except ValueError: return raw
