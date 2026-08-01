from __future__ import annotations

import ast
import math
import multiprocessing
import sys
from dataclasses import dataclass
from multiprocessing.connection import Connection
from typing import Any, ClassVar

from pysl.language.transpiler import SLTranspiler


class SLExecutionError(RuntimeError):
    """Raised when an SL program cannot finish safely."""


class ExecutionLimitExceeded(SLExecutionError):
    """Raised when an SL program exceeds a configured execution limit."""


@dataclass(frozen=True, slots=True)
class ExecutionLimits:
    timeout_seconds: float = 3.0
    max_source_characters: int = 50_000
    max_ast_nodes: int = 5_000
    max_steps: int = 100_000
    max_loop_iterations: int = 10_000
    max_output_characters: int = 100_000
    max_output_lines: int = 10_000
    max_input_items: int = 1_000
    max_input_characters: int = 50_000
    max_value_characters: int = 20_000
    max_collection_items: int = 10_000
    max_integer_bits: int = 4_096
    max_memory_megabytes: int = 1_024


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    output: str
    python_code: str
    variables: dict[str, Any]


class _SafeOperationTransformer(ast.NodeTransformer):
    """Route potentially expansive operations through bounded helpers."""

    _HELPERS: ClassVar[dict[type[ast.operator], str]] = {
        ast.Add: "__suma_segura__",
        ast.Mult: "__multiplicacion_segura__",
        ast.Pow: "__potencia_segura__",
    }

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        helper = self._HELPERS.get(type(node.op))
        if helper is None:
            return node
        replacement = ast.Call(
            func=ast.Name(id=helper, ctx=ast.Load()),
            args=[node.left, node.right],
            keywords=[],
        )
        return ast.copy_location(replacement, node)


class SLExecutor:
    """Execute SL in a validated, isolated process with deterministic limits."""

    _ALLOWED_NODES = (
        ast.Module,
        ast.Assign,
        ast.Name,
        ast.Load,
        ast.Store,
        ast.Constant,
        ast.Expr,
        ast.Call,
        ast.BinOp,
        ast.UnaryOp,
        ast.BoolOp,
        ast.Compare,
        ast.If,
        ast.While,
        ast.For,
        ast.FunctionDef,
        ast.Return,
        ast.arguments,
        ast.arg,
        ast.List,
        ast.Tuple,
        ast.Subscript,
        ast.Slice,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.And,
        ast.Or,
        ast.Not,
        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
    )
    _BUILTIN_CALLS: ClassVar[set[str]] = {
        "int",
        "float",
        "str",
        "range",
        "len",
        "min",
        "max",
        "sum",
    }
    _INTERNAL_CALLS: ClassVar[set[str]] = {"__leer__", "__imprimir__"}
    _RESERVED_NAMES = _BUILTIN_CALLS | _INTERNAL_CALLS | {"__builtins__"}

    def __init__(
        self,
        transpiler: SLTranspiler | None = None,
        limits: ExecutionLimits | None = None,
    ) -> None:
        self._transpiler = transpiler or SLTranspiler()
        self._limits = limits or ExecutionLimits()

    def execute(self, source: str, inputs: list[str] | None = None) -> ExecutionResult:
        self._validate_request(source, inputs or [])
        program = self._transpiler.transpile(source)
        try:
            tree = ast.parse(program.python_code, mode="exec")
            self._validate(tree)
            compile(tree, "<sl>", "exec")
        except SyntaxError as exc:
            raise SLExecutionError(f"El programa SL generado no es válido: {exc.msg}.") from exc

        context = multiprocessing.get_context("spawn")
        receiver, sender = context.Pipe(duplex=False)
        process = context.Process(
            target=_execute_in_child,
            args=(program.python_code, tuple(inputs or []), self._limits, sender),
            name="PySL-SLRuntime",
            daemon=True,
        )
        started = False

        try:
            process.start()
            started = True
            sender.close()
            if not receiver.poll(self._limits.timeout_seconds):
                self._stop_process(process)
                raise ExecutionLimitExceeded(
                    f"La ejecución superó el límite de {self._limits.timeout_seconds:g} segundos."
                )

            try:
                payload = receiver.recv()
            except EOFError as exc:
                raise SLExecutionError(
                    "El proceso aislado finalizó inesperadamente. Revisa los límites del programa."
                ) from exc
            finally:
                process.join(timeout=0.5)

            status, category, message, output, variables = payload
            if status == "error":
                error_type = ExecutionLimitExceeded if category == "limit" else SLExecutionError
                raise error_type(message)
            return ExecutionResult(output, program.python_code, variables)
        finally:
            receiver.close()
            sender.close()
            if started and process.is_alive():
                self._stop_process(process)

    def _validate_request(self, source: str, inputs: list[str]) -> None:
        if len(source) > self._limits.max_source_characters:
            raise ExecutionLimitExceeded(
                "El programa supera el tamaño máximo permitido "
                f"({self._limits.max_source_characters} caracteres)."
            )
        if len(inputs) > self._limits.max_input_items:
            raise ExecutionLimitExceeded("Se proporcionaron demasiados valores de entrada.")
        if sum(len(value) for value in inputs) > self._limits.max_input_characters:
            raise ExecutionLimitExceeded("Las entradas superan el tamaño máximo permitido.")

    def _validate(self, tree: ast.AST) -> None:
        nodes = list(ast.walk(tree))
        if len(nodes) > self._limits.max_ast_nodes:
            raise ExecutionLimitExceeded(
                f"El programa supera el límite de {self._limits.max_ast_nodes} elementos sintácticos."
            )

        declared_functions = {node.name for node in nodes if isinstance(node, ast.FunctionDef)}
        if len(declared_functions) != sum(isinstance(node, ast.FunctionDef) for node in nodes):
            raise SLExecutionError("No se permiten funciones duplicadas.")
        if declared_functions & self._RESERVED_NAMES:
            raise SLExecutionError("Una función utiliza un nombre reservado por el runtime.")

        allowed_calls = self._BUILTIN_CALLS | self._INTERNAL_CALLS | declared_functions
        for node in nodes:
            if not isinstance(node, self._ALLOWED_NODES):
                raise SLExecutionError(f"Construcción no permitida en SL: {type(node).__name__}.")
            if isinstance(node, ast.Name):
                if node.id.startswith("_") and node.id not in self._INTERNAL_CALLS:
                    raise SLExecutionError("Los nombres que comienzan con '_' están reservados.")
                if isinstance(node.ctx, ast.Store) and node.id in self._RESERVED_NAMES:
                    raise SLExecutionError(f"'{node.id}' es un nombre reservado por el runtime.")
            elif isinstance(node, ast.arg) and node.arg.startswith("_"):
                raise SLExecutionError("Los parámetros que comienzan con '_' están reservados.")
            elif isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name) or node.func.id not in allowed_calls:
                    raise SLExecutionError("La llamada solicitada no está permitida.")
                if len(node.args) > 100:
                    raise ExecutionLimitExceeded("Una llamada contiene demasiados argumentos.")
            elif isinstance(node, ast.Constant):
                _ensure_safe_value(node.value, self._limits)

    @staticmethod
    def _stop_process(process: multiprocessing.Process) -> None:
        process.terminate()
        process.join(timeout=0.5)
        if process.is_alive():
            process.kill()
            process.join(timeout=0.5)


def _execute_in_child(
    python_code: str,
    inputs: tuple[str, ...],
    limits: ExecutionLimits,
    connection: Connection,
) -> None:
    try:
        _apply_memory_limit(limits.max_memory_megabytes)
        sys.setrecursionlimit(250)
        tree = ast.parse(python_code, mode="exec")
        tree = ast.fix_missing_locations(_SafeOperationTransformer().visit(tree))
        pending_inputs = iter(inputs)
        output_lines: list[str] = []
        output_characters = 0
        steps = 0

        def trace_steps(_frame: Any, event: str, _argument: Any) -> Any:
            nonlocal steps
            if event in {"call", "line"}:
                steps += 1
                if steps > limits.max_steps:
                    raise ExecutionLimitExceeded(
                        f"El programa superó el límite de {limits.max_steps} pasos."
                    )
            return trace_steps

        def read_value() -> object:
            try:
                raw_value = next(pending_inputs)
            except StopIteration as exc:
                raise SLExecutionError(
                    "El programa solicitó más entradas de las proporcionadas."
                ) from exc
            return _coerce(raw_value, limits)

        def print_value(*values: object) -> None:
            nonlocal output_characters
            if len(output_lines) >= limits.max_output_lines:
                raise ExecutionLimitExceeded(
                    f"La salida superó el límite de {limits.max_output_lines} líneas."
                )
            for value in values:
                _ensure_safe_value(value, limits)
            line = " ".join(str(value) for value in values)
            projected_size = output_characters + len(line) + int(bool(output_lines))
            if projected_size > limits.max_output_characters:
                raise ExecutionLimitExceeded(
                    f"La salida superó el límite de {limits.max_output_characters} caracteres."
                )
            output_lines.append(line)
            output_characters = projected_size

        def safe_range(*values: int) -> range:
            result = range(*values)
            try:
                iterations = len(result)
            except OverflowError as exc:
                raise ExecutionLimitExceeded("El ciclo solicitado es demasiado grande.") from exc
            if iterations > limits.max_loop_iterations:
                raise ExecutionLimitExceeded(
                    f"Un ciclo supera el límite de {limits.max_loop_iterations} iteraciones."
                )
            return result

        def safe_int(value: object = 0) -> int:
            result = int(value)  # type: ignore[arg-type]
            _ensure_safe_value(result, limits)
            return result

        def safe_float(value: object = 0) -> float:
            result = float(value)  # type: ignore[arg-type]
            _ensure_safe_value(result, limits)
            return result

        def safe_str(value: object = "") -> str:
            _ensure_safe_value(value, limits)
            result = str(value)
            _ensure_safe_value(result, limits)
            return result

        def safe_sum(values: object) -> object:
            if not isinstance(values, (list, tuple, range)):
                raise SLExecutionError("sum requiere un vector o rango permitido.")
            result = sum(values)
            _ensure_safe_value(result, limits)
            return result

        environment: dict[str, Any] = {
            "__builtins__": {},
            "__leer__": read_value,
            "__imprimir__": print_value,
            "__suma_segura__": lambda left, right: _safe_add(left, right, limits),
            "__multiplicacion_segura__": lambda left, right: _safe_multiply(left, right, limits),
            "__potencia_segura__": lambda base, exponent: _safe_power(base, exponent, limits),
            "int": safe_int,
            "float": safe_float,
            "str": safe_str,
            "range": safe_range,
            "len": len,
            "min": min,
            "max": max,
            "sum": safe_sum,
        }

        sys.settrace(trace_steps)
        try:
            exec(compile(tree, "<sl>", "exec"), environment, environment)
        finally:
            sys.settrace(None)

        excluded = {
            "int",
            "float",
            "str",
            "range",
            "len",
            "min",
            "max",
            "sum",
        }
        variables = {
            key: value
            for key, value in environment.items()
            if not key.startswith("__") and key not in excluded and not callable(value)
        }
        for value in variables.values():
            _ensure_safe_value(value, limits)
        connection.send(("ok", "", "", "\n".join(output_lines), variables))
    except ExecutionLimitExceeded as exc:
        connection.send(("error", "limit", str(exc), "", {}))
    except (
        ArithmeticError,
        IndexError,
        NameError,
        RecursionError,
        SLExecutionError,
        TypeError,
    ) as exc:
        connection.send(("error", "runtime", f"Error de ejecución: {exc}", "", {}))
    except MemoryError:
        connection.send(("error", "limit", "El programa superó el límite de memoria.", "", {}))
    except Exception as exc:  # pragma: no cover - defensive child-process boundary
        connection.send(("error", "runtime", f"El runtime rechazó el programa: {exc}", "", {}))
    finally:
        connection.close()


def _safe_add(left: object, right: object, limits: ExecutionLimits) -> object:
    if isinstance(left, (str, list, tuple)) and isinstance(right, type(left)):
        if len(left) + len(right) > limits.max_collection_items:
            raise ExecutionLimitExceeded("La suma produciría una colección demasiado grande.")
    result = left + right  # type: ignore[operator]
    _ensure_safe_value(result, limits)
    return result


def _safe_multiply(left: object, right: object, limits: ExecutionLimits) -> object:
    sequence: str | list[object] | tuple[object, ...] | None = None
    factor: int | None = None
    if isinstance(left, (str, list, tuple)) and isinstance(right, int):
        sequence, factor = left, right
    elif isinstance(right, (str, list, tuple)) and isinstance(left, int):
        sequence, factor = right, left
    if sequence is not None and factor is not None:
        if len(sequence) * max(0, factor) > limits.max_collection_items:
            raise ExecutionLimitExceeded(
                "La multiplicación produciría una colección demasiado grande."
            )
    result = left * right  # type: ignore[operator]
    _ensure_safe_value(result, limits)
    return result


def _safe_power(base: object, exponent: object, limits: ExecutionLimits) -> object:
    if not isinstance(base, (int, float)) or not isinstance(exponent, (int, float)):
        raise SLExecutionError("La potencia solo admite valores numéricos.")
    if abs(exponent) > 1_000:
        raise ExecutionLimitExceeded("El exponente supera el límite permitido.")
    if isinstance(base, int) and isinstance(exponent, int) and exponent > 0:
        estimated_bits = max(1, base.bit_length()) * exponent
        if estimated_bits > limits.max_integer_bits:
            raise ExecutionLimitExceeded("La potencia produciría un entero demasiado grande.")
    try:
        result = base**exponent
    except OverflowError as exc:
        raise ExecutionLimitExceeded("La potencia supera el límite numérico.") from exc
    _ensure_safe_value(result, limits)
    return result


def _coerce(raw: str, limits: ExecutionLimits) -> object:
    value = raw.strip()
    if value.casefold() in {"verdadero", "true"}:
        return True
    if value.casefold() in {"falso", "false"}:
        return False
    try:
        result: object = int(value)
    except ValueError:
        try:
            result = float(value)
        except ValueError:
            result = raw
    _ensure_safe_value(result, limits)
    return result


def _ensure_safe_value(
    value: object,
    limits: ExecutionLimits,
    *,
    _remaining_items: list[int] | None = None,
) -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        if value.bit_length() > limits.max_integer_bits:
            raise ExecutionLimitExceeded("Un entero supera el tamaño máximo permitido.")
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ExecutionLimitExceeded("El resultado numérico no es finito.")
        return
    if isinstance(value, str):
        if len(value) > limits.max_value_characters:
            raise ExecutionLimitExceeded("Un texto supera el tamaño máximo permitido.")
        return
    if isinstance(value, (list, tuple)):
        remaining_items = _remaining_items or [limits.max_collection_items]
        remaining_items[0] -= len(value)
        if remaining_items[0] < 0:
            raise ExecutionLimitExceeded("Una colección supera el tamaño máximo permitido.")
        for item in value:
            _ensure_safe_value(item, limits, _remaining_items=remaining_items)
        return
    raise SLExecutionError(f"Tipo de valor no permitido: {type(value).__name__}.")


def _apply_memory_limit(maximum_megabytes: int) -> None:
    if sys.platform == "win32":
        return
    try:
        import resource

        maximum_bytes = maximum_megabytes * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (maximum_bytes, maximum_bytes))
    except (ImportError, OSError, ValueError):
        return
