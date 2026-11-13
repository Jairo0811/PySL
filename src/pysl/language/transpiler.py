from __future__ import annotations

import ast
import io
import keyword
import re
import tokenize
from dataclasses import dataclass
from typing import ClassVar


class TranspilationError(ValueError):
    """Raised when SL source code cannot be translated.

    ``line`` is the first SL line number mentioned in the message (or ``None``), so the
    interface can point the student at the offending line.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        match = re.search(r"línea (\d+)", message)
        self.line: int | None = int(match.group(1)) if match else None


@dataclass(frozen=True, slots=True)
class TranspiledProgram:
    python_code: str
    # line_map[n - 1] is the SL source line that produced line n of ``python_code``.
    line_map: tuple[int, ...] = ()

    def sl_line(self, python_line: int | None) -> int | None:
        """Translate a generated Python line number back to the SL source line."""
        if python_line is None or not 1 <= python_line <= len(self.line_map):
            return None
        return self.line_map[python_line - 1]


@dataclass(slots=True)
class _BlockState:
    kind: str
    line: int
    has_body: bool = False
    has_else: bool = False


class SLTranspiler:
    """Translate the stable SL 1.0 educational syntax to restricted Python."""

    _BLOCK_ENDINGS: ClassVar[dict[str, str]] = {
        "finsi": "si",
        "finmientras": "mientras",
        "finpara": "para",
        "finfuncion": "funcion",
    }
    _LOGICAL_NAMES: ClassVar[dict[str, str]] = {
        "verdadero": "True",
        "falso": "False",
        "y": "and",
        "o": "or",
        "no": "not",
    }

    def transpile(self, source: str) -> TranspiledProgram:
        output: list[str] = []
        line_map: list[int] = []
        indent = 0
        saw_start = False
        saw_end = False
        block_stack: list[_BlockState] = []

        for number, raw_line in enumerate(source.splitlines(), start=1):
            comment_start = self.comment_start(raw_line)
            code = raw_line if comment_start is None else raw_line[:comment_start]
            line = code.strip()
            if not line:
                continue

            normalized = line.casefold()
            if normalized == "inicio":
                if saw_start:
                    raise TranspilationError(f"'inicio' repetido en la línea {number}.")
                if block_stack:
                    raise TranspilationError(
                        f"'inicio' no puede aparecer dentro de un bloque en la línea {number}."
                    )
                saw_start = True
                continue

            if normalized == "fin":
                if not saw_start:
                    raise TranspilationError(
                        f"'fin' aparece antes de 'inicio' en la línea {number}."
                    )
                if saw_end:
                    raise TranspilationError(f"'fin' repetido en la línea {number}.")
                if block_stack:
                    raise TranspilationError(
                        f"Se debe cerrar '{block_stack[-1].kind}' antes de 'fin' "
                        f"en la línea {number}."
                    )
                saw_end = True
                continue

            if saw_end:
                raise TranspilationError(
                    f"No se permiten instrucciones después de 'fin' (línea {number})."
                )

            if normalized in self._BLOCK_ENDINGS:
                if not block_stack:
                    raise TranspilationError(f"Bloque cerrado de más en la línea {number}.")
                expected = self._BLOCK_ENDINGS[normalized]
                current = block_stack[-1]
                if current.kind != expected:
                    raise TranspilationError(
                        f"Se esperaba cerrar '{current.kind}' antes de '{normalized}' "
                        f"en la línea {number}."
                    )
                if not current.has_body:
                    raise TranspilationError(
                        f"El bloque '{current.kind}' de la línea {current.line} está vacío."
                    )
                block_stack.pop()
                indent -= 1
                continue

            if normalized == "sino":
                if not block_stack or block_stack[-1].kind != "si":
                    raise TranspilationError(f"'sino' sin un bloque 'si' en la línea {number}.")
                current = block_stack[-1]
                if current.has_else:
                    raise TranspilationError(f"'sino' repetido en la línea {number}.")
                if not current.has_body:
                    raise TranspilationError(
                        f"El bloque 'si' de la línea {current.line} está vacío."
                    )
                current.has_else = True
                current.has_body = False
                indent -= 1
                output.append(self._indent(indent) + "else:")
                line_map.append(number)
                indent += 1
                continue

            if not saw_start and not any(block.kind == "funcion" for block in block_stack):
                if not re.match(r"funcion\b", line, re.IGNORECASE):
                    raise TranspilationError(
                        f"La instrucción de la línea {number} debe estar dentro de 'inicio' y 'fin'."
                    )

            translated, opens = self._translate_statement(line, number)
            if block_stack:
                block_stack[-1].has_body = True
            output.append(self._indent(indent) + translated)
            line_map.append(number)
            if opens:
                block_stack.append(_BlockState(opens, number))
                indent += 1

        if block_stack:
            raise TranspilationError(
                f"Bloque sin cerrar: '{block_stack[-1].kind}' (línea {block_stack[-1].line})."
            )
        if not saw_start or not saw_end:
            raise TranspilationError("Todo programa SL debe contener 'inicio' y 'fin'.")
        return TranspiledProgram("\n".join(output) + "\n", tuple(line_map))

    def _translate_statement(self, line: str, number: int) -> tuple[str, str | None]:
        read_match = re.fullmatch(r"leer\s*\(\s*([A-Za-z_]\w*)\s*\)", line, re.IGNORECASE)
        if read_match:
            return f"{self._name(read_match.group(1), number)} = __leer__()", None

        print_match = re.fullmatch(r"imprimir\s*\((.*)\)", line, re.IGNORECASE)
        if print_match:
            arguments = print_match.group(1)
            if not arguments.strip():
                return "__imprimir__()", None
            return f"__imprimir__({self._expression(arguments, number)})", None

        if_match = re.fullmatch(r"si\s+(.+?)(?:\s+entonces)?", line, re.IGNORECASE)
        if if_match:
            return f"if {self._expression(if_match.group(1), number)}:", "si"

        while_match = re.fullmatch(r"mientras\s+(.+)", line, re.IGNORECASE)
        if while_match:
            return f"while {self._expression(while_match.group(1), number)}:", "mientras"

        for_match = re.fullmatch(
            r"para\s+([A-Za-z_]\w*)\s+desde\s+(.+?)\s+hasta\s+(.+)",
            line,
            re.IGNORECASE,
        )
        if for_match:
            name, start, end = for_match.groups()
            self._name(name, number)
            start_expression = self._expression(start, number)
            end_expression = self._expression(end, number)
            return (
                f"for {name} in range(int({start_expression}), int({end_expression}) + 1):",
                "para",
            )

        function_match = re.fullmatch(r"funcion\s+([A-Za-z_]\w*)\s*\((.*?)\)", line, re.IGNORECASE)
        if function_match:
            name, raw_parameters = function_match.groups()
            self._name(name, number)
            parameters = [parameter.strip() for parameter in raw_parameters.split(",")]
            if parameters == [""]:
                parameters = []
            if any(not re.fullmatch(r"[A-Za-z_]\w*", parameter) for parameter in parameters):
                raise TranspilationError(f"Parámetros inválidos en la línea {number}.")
            if len(parameters) != len(set(parameters)):
                raise TranspilationError(f"Hay parámetros duplicados en la línea {number}.")
            for parameter in parameters:
                self._name(parameter, number)
            return f"def {name}({', '.join(parameters)}):", "funcion"

        return_match = re.fullmatch(r"retornar(?:\s+(.+))?", line, re.IGNORECASE)
        if return_match:
            value = return_match.group(1)
            return (
                f"return {self._expression(value, number)}" if value else "return",
                None,
            )

        index_assignment = re.fullmatch(r"([A-Za-z_]\w*)\s*\[\s*(.+?)\s*\]\s*=\s*(.+)", line)
        if index_assignment:
            name, index, value = index_assignment.groups()
            self._name(name, number)
            return (
                f"{name}[{self._expression(index, number)}] = {self._expression(value, number)}",
                None,
            )

        assignment = re.fullmatch(r"([A-Za-z_]\w*)\s*=\s*(.+)", line)
        if assignment:
            return (
                f"{self._name(assignment.group(1), number)} = "
                f"{self._expression(assignment.group(2), number)}",
                None,
            )

        declaration = re.fullmatch(
            r"(?:numerico|entero|real|cadena|logico|caracter|vector)\s+"
            r"([A-Za-z_]\w*)(?:\s*=\s*(.+))?",
            line,
            re.IGNORECASE,
        )
        if declaration:
            name, value = declaration.groups()
            self._name(name, number)
            return f"{name} = {self._expression(value, number) if value else 'None'}", None

        call = re.fullmatch(r"([A-Za-z_]\w*)\s*\((.*)\)", line)
        if call:
            return f"{call.group(1)}({self._expression(call.group(2), number)})", None

        raise TranspilationError(f"Instrucción no reconocida en la línea {number}: {line}")

    def _expression(self, expression: str | None, line: int) -> str:
        if expression is None:
            return "None"

        try:
            tokens = tokenize.generate_tokens(io.StringIO(expression.strip()).readline)
            translated_tokens: list[tokenize.TokenInfo] = []
            for token in tokens:
                replacement = token.string
                if token.type == tokenize.NAME:
                    replacement = self._LOGICAL_NAMES.get(token.string.casefold(), token.string)
                elif token.type == tokenize.OP and token.string == "<>":
                    replacement = "!="
                translated_tokens.append(token._replace(string=replacement))
            translated = tokenize.untokenize(translated_tokens).strip()
            ast.parse(translated, mode="eval")
        except (IndentationError, SyntaxError, tokenize.TokenError) as exc:
            raise TranspilationError(
                f"Expresión inválida en la línea {line}: {expression}"
            ) from exc
        return translated

    @staticmethod
    def comment_start(text: str) -> int | None:
        """Return the column where a comment begins on ``text``, or ``None``.

        ``//`` only starts a comment at the beginning of a line, because anywhere else it is
        the integer-division operator. ``#`` starts a comment anywhere outside a string.
        """
        stripped = text.lstrip()
        if stripped.startswith("//"):
            return len(text) - len(stripped)
        quote: str | None = None
        escaped = False
        for index, character in enumerate(text):
            if quote is not None:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
            elif character in {'"', "'"}:
                quote = character
            elif character == "#":
                return index
        return None

    @staticmethod
    def _name(identifier: str, line: int) -> str:
        """Reject names that are reserved words in the generated Python."""
        if keyword.iskeyword(identifier):
            raise TranspilationError(
                f"'{identifier}' es una palabra reservada y no puede usarse como nombre "
                f"(línea {line})."
            )
        return identifier

    @staticmethod
    def _indent(level: int) -> str:
        return "    " * level
