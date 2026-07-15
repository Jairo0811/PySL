import re
from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat

class PySLHighlighter(QSyntaxHighlighter):
    def __init__(self, document) -> None:
        super().__init__(document)
        self.rules = []
        def fmt(color, bold=False):
            f = QTextCharFormat(); f.setForeground(QColor(color));
            if bold: f.setFontWeight(700)
            return f
        keyword = fmt("#c084fc", True); builtin = fmt("#60a5fa"); string = fmt("#fbbf24"); comment = fmt("#64748b")
        for word in "inicio fin si entonces sino finsi mientras finmientras para desde hasta finpara funcion finfuncion retornar numerico entero real cadena logico caracter vector verdadero falso y o no".split():
            self.rules.append((re.compile(rf"\b{word}\b", re.I), keyword))
        for word in ("leer", "imprimir", "len", "min", "max", "sum"):
            self.rules.append((re.compile(rf"\b{word}\b", re.I), builtin))
        self.rules += [(re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), string), (re.compile(r"//.*$|#.*$"), comment)]
    def highlightBlock(self, text: str) -> None:
        for regex, form in self.rules:
            for match in regex.finditer(text): self.setFormat(match.start(), match.end()-match.start(), form)
