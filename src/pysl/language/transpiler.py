from __future__ import annotations

import re
from dataclasses import dataclass


class TranspilationError(ValueError):
    """Raised when PySL source code cannot be translated."""


@dataclass(frozen=True, slots=True)
class TranspiledProgram:
    python_code: str


class PySLTranspiler:
    """Translate the stable PySL 1.0 educational syntax to restricted Python."""

    _BLOCK_ENDINGS = {"finsi", "finmientras", "finpara", "finfuncion"}

    def transpile(self, source: str) -> TranspiledProgram:
        output: list[str] = []
        indent = 0
        saw_start = False
        saw_end = False
        block_stack: list[str] = []

        for number, raw_line in enumerate(source.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue
            normalized = line.lower()
            if normalized == "inicio":
                saw_start = True
                continue
            if normalized == "fin":
                saw_end = True
                continue
            if normalized in self._BLOCK_ENDINGS:
                if not block_stack:
                    raise TranspilationError(f"Bloque cerrado de más en la línea {number}.")
                expected = {"finsi":"si", "finmientras":"mientras", "finpara":"para", "finfuncion":"funcion"}[normalized]
                actual = block_stack.pop()
                if actual != expected:
                    raise TranspilationError(f"Se esperaba cerrar '{actual}' antes de '{normalized}' en la línea {number}.")
                indent -= 1
                continue
            if normalized == "sino":
                if not block_stack or block_stack[-1] != "si":
                    raise TranspilationError(f"'sino' sin un bloque 'si' en la línea {number}.")
                indent -= 1
                output.append(self._indent(indent) + "else:")
                indent += 1
                continue

            translated, opens = self._translate_statement(line, number)
            output.append(self._indent(indent) + translated)
            if opens:
                block_stack.append(opens)
                indent += 1

        if block_stack:
            raise TranspilationError(f"Bloque sin cerrar: {block_stack[-1]}.")
        if not saw_start or not saw_end:
            raise TranspilationError("Todo programa PySL debe contener 'inicio' y 'fin'.")
        return TranspiledProgram("\n".join(output) + "\n")

    def _translate_statement(self, line: str, number: int) -> tuple[str, str | None]:
        read_match = re.fullmatch(r"leer\s*\(\s*([A-Za-z_]\w*)\s*\)", line, re.I)
        if read_match:
            return f"{read_match.group(1)} = __leer__()", None
        print_match = re.fullmatch(r"imprimir\s*\((.*)\)", line, re.I)
        if print_match:
            return f"__imprimir__({self._expression(print_match.group(1))})", None
        if_match = re.fullmatch(r"si\s+(.+?)(?:\s+entonces)?", line, re.I)
        if if_match:
            return f"if {self._expression(if_match.group(1))}:", "si"
        while_match = re.fullmatch(r"mientras\s+(.+)", line, re.I)
        if while_match:
            return f"while {self._expression(while_match.group(1))}:", "mientras"
        for_match = re.fullmatch(r"para\s+([A-Za-z_]\w*)\s+desde\s+(.+?)\s+hasta\s+(.+)", line, re.I)
        if for_match:
            name, start, end = for_match.groups()
            return f"for {name} in range(int({self._expression(start)}), int({self._expression(end)}) + 1):", "para"
        function_match = re.fullmatch(r"funcion\s+([A-Za-z_]\w*)\s*\((.*?)\)", line, re.I)
        if function_match:
            return f"def {function_match.group(1)}({function_match.group(2)}):", "funcion"
        return_match = re.fullmatch(r"retornar(?:\s+(.+))?", line, re.I)
        if return_match:
            value = return_match.group(1)
            return (f"return {self._expression(value)}" if value else "return"), None
        index_assignment = re.fullmatch(r"([A-Za-z_]\w*)\s*\[\s*(.+?)\s*\]\s*=\s*(.+)", line)
        if index_assignment:
            name, index, value = index_assignment.groups()
            return f"{name}[{self._expression(index)}] = {self._expression(value)}", None
        assignment = re.fullmatch(r"([A-Za-z_]\w*)\s*=\s*(.+)", line)
        if assignment:
            return f"{assignment.group(1)} = {self._expression(assignment.group(2))}", None
        declaration = re.fullmatch(r"(?:numerico|entero|real|cadena|logico|caracter|vector)\s+([A-Za-z_]\w*)(?:\s*=\s*(.+))?", line, re.I)
        if declaration:
            name, value = declaration.groups()
            return f"{name} = {self._expression(value) if value else 'None'}", None
        call = re.fullmatch(r"([A-Za-z_]\w*)\s*\((.*)\)", line)
        if call:
            return f"{call.group(1)}({self._expression(call.group(2))})", None
        raise TranspilationError(f"Instrucción no reconocida en la línea {number}: {line}")

    @staticmethod
    def _expression(expression: str | None) -> str:
        if expression is None:
            return "None"
        padded = f" {expression.strip()} "
        replacements = ((r"\bverdadero\b", "True"), (r"\bfalso\b", "False"),
                        (r"\by\b", "and"), (r"\bo\b", "or"), (r"\bno\b", "not"),
                        (r"<>", "!="))
        for pattern, replacement in replacements:
            padded = re.sub(pattern, replacement, padded, flags=re.I)
        return padded.strip()

    @staticmethod
    def _indent(level: int) -> str:
        return "    " * level
