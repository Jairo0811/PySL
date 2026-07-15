from __future__ import annotations

import re

from pysl.language.transpiler import PySLTranspiler


class CodeConverter:
    def __init__(self) -> None:
        self._transpiler = PySLTranspiler()

    def pysl_to_python(self, source: str) -> str:
        return self._transpiler.transpile(source).python_code

    def python_to_pysl(self, source: str) -> str:
        result = ["inicio"]
        indent_stack: list[str] = []
        for raw in source.splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            level = (len(raw) - len(raw.lstrip())) // 4
            while len(indent_stack) > level:
                result.append(indent_stack.pop())
            if match := re.fullmatch(r"print\((.*)\)", stripped):
                result.append(f"imprimir({match.group(1)})")
            elif match := re.fullmatch(
                r"([A-Za-z_]\w*)\s*=\s*(?:int\()?input\([^)]*\)\)?", stripped
            ):
                result.append(f"leer({match.group(1)})")
            elif match := re.fullmatch(r"if\s+(.+):", stripped):
                result.append(f"si {match.group(1)} entonces")
                indent_stack.append("finsi")
            elif stripped == "else:":
                if indent_stack and indent_stack[-1] == "finsi":
                    result.append("sino")
            elif match := re.fullmatch(r"while\s+(.+):", stripped):
                result.append(f"mientras {match.group(1)}")
                indent_stack.append("finmientras")
            elif match := re.fullmatch(
                r"for\s+(\w+)\s+in\s+range\((.+),\s*(.+)\s*\+\s*1\):", stripped
            ):
                result.append(
                    f"para {match.group(1)} desde {match.group(2)} hasta {match.group(3)}"
                )
                indent_stack.append("finpara")
            else:
                result.append(stripped)
        while indent_stack:
            result.append(indent_stack.pop())
        result.append("fin")
        return "\n".join(result)
