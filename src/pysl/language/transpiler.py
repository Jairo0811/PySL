from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass
from typing import ClassVar


class TranspilationError(ValueError):
    """Raised when SL source code cannot be translated."""


@dataclass(frozen=True, slots=True)
class TranspiledProgram:
    python_code: str


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
        indent = 0
        saw_start = False
        saw_end = False
        block_stack: list[_BlockState] = []

        for number, raw_line in enumerate(source.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith(("//", "#")):
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
            if opens:
                block_stack.append(_BlockState(opens, number))
                indent += 1

        if block_stack:
            raise TranspilationError(
                f"Bloque sin cerrar: '{block_stack[-1].kind}' (línea {block_stack[-1].line})."
            )
        if not saw_start or not saw_end:
            raise TranspilationError("Todo programa SL debe contener 'inicio' y 'fin'.")
        return TranspiledProgram("\n".join(output) + "\n")

    def _translate_statement(self, line: str, number: int) -> tuple[str, str | None]:
        read_match = re.fullmatch(r"leer\s*\(\s*([A-Za-z_]\w*)\s*\)", line, re.IGNORECASE)
        if read_match:
            return f"{read_match.group(1)} = __leer__()", None

        print_match = re.fullmatch(r"imprimir\s*\((.*)\)", line, re.IGNORECASE)
        if print_match:
            return f"__imprimir__({self._expression(print_match.group(1), number)})", None

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
            start_expression = self._expression(start, number)
            end_expression = self._expression(end, number)
            return (
                f"for {name} in range(int({start_expression}), int({end_expression}) + 1):",
                "para",
            )

        function_match = re.fullmatch(r"funcion\s+([A-Za-z_]\w*)\s*\((.*?)\)", line, re.IGNORECASE)
        if function_match:
            name, raw_parameters = function_match.groups()
            parameters = [parameter.strip() for parameter in raw_parameters.split(",")]
            if parameters == [""]:
                parameters = []
            if any(not re.fullmatch(r"[A-Za-z_]\w*", parameter) for parameter in parameters):
                raise TranspilationError(f"Parámetros inválidos en la línea {number}.")
            if len(parameters) != len(set(parameters)):
                raise TranspilationError(f"Hay parámetros duplicados en la línea {number}.")
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
            return (
                f"{name}[{self._expression(index, number)}] = {self._expression(value, number)}",
                None,
            )

        assignment = re.fullmatch(r"([A-Za-z_]\w*)\s*=\s*(.+)", line)
        if assignment:
            return (
                f"{assignment.group(1)} = {self._expression(assignment.group(2), number)}",
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
    def _indent(level: int) -> str:
        return "    " * level
