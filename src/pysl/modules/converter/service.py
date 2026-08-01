from __future__ import annotations

import ast
import io
import tokenize
from typing import ClassVar

from pysl.language.transpiler import SLTranspiler


class ConversionError(ValueError):
    """Raised when source code uses a construct outside the educational subset."""


class CodeConverter:
    """Convert between SL and the supported structured subset of Python."""

    _EXPRESSION_NODES = (
        ast.Expression,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.List,
        ast.Tuple,
        ast.Subscript,
        ast.Slice,
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.Call,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Not,
        ast.And,
        ast.Or,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
    )
    _PYTHON_TO_SL_NAMES: ClassVar[dict[str, str]] = {
        "True": "verdadero",
        "False": "falso",
        "and": "y",
        "or": "o",
        "not": "no",
    }

    def __init__(self) -> None:
        self._transpiler = SLTranspiler()

    def sl_to_python(self, source: str) -> str:
        return self._transpiler.transpile(source).python_code

    def python_to_sl(self, source: str) -> str:
        try:
            tree = ast.parse(source, mode="exec")
        except SyntaxError as exc:
            raise ConversionError(f"Python no válido en la línea {exc.lineno}: {exc.msg}.") from exc

        functions = [statement for statement in tree.body if isinstance(statement, ast.FunctionDef)]
        main_statements = [
            statement for statement in tree.body if not isinstance(statement, ast.FunctionDef)
        ]
        result: list[str] = []
        result.extend(self._convert_statements(functions, 0))
        if functions:
            result.append("")
        result.append("inicio")
        result.extend(self._convert_statements(main_statements, 1))
        result.append("fin")
        return "\n".join(result)

    def _convert_statements(self, statements: list[ast.stmt], indent: int) -> list[str]:
        result: list[str] = []
        for statement in statements:
            result.extend(self._convert_statement(statement, indent))
        return result

    def _convert_statement(self, statement: ast.stmt, indent: int) -> list[str]:
        prefix = "    " * indent

        if isinstance(statement, ast.FunctionDef):
            if statement.decorator_list:
                raise ConversionError("Python → SL no admite decoradores.")
            arguments = statement.args
            if (
                arguments.posonlyargs
                or arguments.kwonlyargs
                or arguments.vararg
                or arguments.kwarg
                or arguments.defaults
                or arguments.kw_defaults
            ):
                raise ConversionError(
                    "Python → SL solo admite parámetros posicionales sin valores predeterminados."
                )
            parameter_names = ", ".join(argument.arg for argument in arguments.args)
            lines = [f"{prefix}funcion {statement.name}({parameter_names})"]
            lines.extend(self._require_body(statement.body, indent + 1, "funcion"))
            lines.append(f"{prefix}finfuncion")
            return lines

        if isinstance(statement, ast.Assign):
            if len(statement.targets) != 1:
                raise ConversionError("Python → SL no admite asignaciones múltiples.")
            target = self._target(statement.targets[0])
            if self._is_input_call(statement.value):
                if not isinstance(statement.targets[0], ast.Name):
                    raise ConversionError("leer requiere una variable simple como destino.")
                return [f"{prefix}leer({target})"]
            return [f"{prefix}{target} = {self._expression(statement.value)}"]

        if isinstance(statement, ast.AnnAssign):
            target = self._target(statement.target)
            value = "None" if statement.value is None else self._expression(statement.value)
            return [f"{prefix}{target} = {value}"]

        if isinstance(statement, ast.AugAssign):
            target = self._target(statement.target)
            operation = ast.BinOp(left=statement.target, op=statement.op, right=statement.value)
            return [f"{prefix}{target} = {self._expression(operation)}"]

        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
            call = statement.value
            if isinstance(call.func, ast.Name) and call.func.id == "print":
                if call.keywords:
                    raise ConversionError("Python → SL no admite opciones sep/end de print.")
                arguments = ", ".join(self._expression(argument) for argument in call.args)
                return [f"{prefix}imprimir({arguments})"]
            return [f"{prefix}{self._expression(call)}"]

        if isinstance(statement, ast.If):
            lines = [f"{prefix}si {self._expression(statement.test)} entonces"]
            lines.extend(self._require_body(statement.body, indent + 1, "si"))
            if statement.orelse:
                lines.append(f"{prefix}sino")
                lines.extend(self._require_body(statement.orelse, indent + 1, "sino"))
            lines.append(f"{prefix}finsi")
            return lines

        if isinstance(statement, ast.While):
            if statement.orelse:
                raise ConversionError("Python → SL no admite else asociado a while.")
            lines = [f"{prefix}mientras {self._expression(statement.test)}"]
            lines.extend(self._require_body(statement.body, indent + 1, "mientras"))
            lines.append(f"{prefix}finmientras")
            return lines

        if isinstance(statement, ast.For):
            if statement.orelse:
                raise ConversionError("Python → SL no admite else asociado a for.")
            if not isinstance(statement.target, ast.Name):
                raise ConversionError("Python → SL requiere una variable simple en for.")
            start, end = self._range_bounds(statement.iter)
            lines = [f"{prefix}para {statement.target.id} desde {start} hasta {end}"]
            lines.extend(self._require_body(statement.body, indent + 1, "para"))
            lines.append(f"{prefix}finpara")
            return lines

        if isinstance(statement, ast.Return):
            value = "" if statement.value is None else f" {self._expression(statement.value)}"
            return [f"{prefix}retornar{value}"]

        raise ConversionError(
            f"Python → SL no admite la construcción {type(statement).__name__} "
            f"(línea {getattr(statement, 'lineno', '?')})."
        )

    def _require_body(self, body: list[ast.stmt], indent: int, block_name: str) -> list[str]:
        if not body:
            raise ConversionError(f"El bloque {block_name} está vacío.")
        return self._convert_statements(body, indent)

    def _range_bounds(self, expression: ast.expr) -> tuple[str, str]:
        if not (
            isinstance(expression, ast.Call)
            and isinstance(expression.func, ast.Name)
            and expression.func.id == "range"
            and not expression.keywords
        ):
            raise ConversionError("Python → SL solo convierte ciclos for basados en range.")
        if len(expression.args) == 1:
            return "0", f"({self._expression(expression.args[0])}) - 1"
        if len(expression.args) == 2:
            start = self._expression(expression.args[0])
            stop = expression.args[1]
            if (
                isinstance(stop, ast.BinOp)
                and isinstance(stop.op, ast.Add)
                and isinstance(stop.right, ast.Constant)
                and stop.right.value == 1
            ):
                return start, self._expression(stop.left)
            return start, f"({self._expression(stop)}) - 1"
        raise ConversionError("Python → SL solo admite range(límite) o range(inicio, límite).")

    def _target(self, target: ast.expr) -> str:
        if isinstance(target, ast.Name) and not target.id.startswith("_"):
            return target.id
        if isinstance(target, ast.Subscript):
            return self._expression(target)
        raise ConversionError("Python → SL encontró un destino de asignación no compatible.")

    @staticmethod
    def _is_input_call(expression: ast.expr) -> bool:
        candidate = expression
        if (
            isinstance(candidate, ast.Call)
            and isinstance(candidate.func, ast.Name)
            and candidate.func.id in {"int", "float", "str"}
            and len(candidate.args) == 1
            and not candidate.keywords
        ):
            candidate = candidate.args[0]
        return (
            isinstance(candidate, ast.Call)
            and isinstance(candidate.func, ast.Name)
            and candidate.func.id == "input"
            and len(candidate.args) <= 1
            and not candidate.keywords
        )

    def _expression(self, expression: ast.expr) -> str:
        for node in ast.walk(expression):
            if not isinstance(node, self._EXPRESSION_NODES):
                raise ConversionError(
                    f"Python → SL no admite {type(node).__name__} dentro de expresiones."
                )
            if isinstance(node, ast.Name) and node.id.startswith("_"):
                raise ConversionError("Python → SL no admite nombres privados.")
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.keywords:
                    raise ConversionError("Python → SL solo admite llamadas simples sin keywords.")

        python_expression = ast.unparse(expression)
        tokens = tokenize.generate_tokens(io.StringIO(python_expression).readline)
        translated_tokens: list[tokenize.TokenInfo] = []
        for token in tokens:
            replacement = token.string
            if token.type == tokenize.NAME:
                replacement = self._PYTHON_TO_SL_NAMES.get(token.string, token.string)
            elif token.type == tokenize.OP and token.string == "!=":
                replacement = "<>"
            translated_tokens.append(token._replace(string=replacement))
        return tokenize.untokenize(translated_tokens).strip()
