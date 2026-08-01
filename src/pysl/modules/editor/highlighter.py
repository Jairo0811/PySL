import re
from typing import Any

from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat


class SLHighlighter(QSyntaxHighlighter):
    """Highlight the supported SL 1.0 syntax."""

    def __init__(self, document: Any) -> None:
        super().__init__(document)
        self.rules: list[tuple[re.Pattern[str], QTextCharFormat]] = []

        keyword = self._format("#c084fc", bold=True)
        builtin = self._format("#60a5fa")
        string = self._format("#fbbf24")
        comment = self._format("#64748b")
        keywords = (
            "inicio fin si entonces sino finsi mientras finmientras para desde hasta "
            "finpara funcion finfuncion retornar numerico entero real cadena logico "
            "caracter vector verdadero falso y o no"
        )
        for word in keywords.split():
            self.rules.append((re.compile(rf"\b{word}\b", re.IGNORECASE), keyword))
        for word in ("leer", "imprimir", "len", "min", "max", "sum"):
            self.rules.append((re.compile(rf"\b{word}\b", re.IGNORECASE), builtin))
        self.rules.extend(
            (
                (re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"'), string),
                (re.compile(r"//.*$|#.*$"), comment),
            )
        )

    @staticmethod
    def _format(color: str, *, bold: bool = False) -> QTextCharFormat:
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        if bold:
            text_format.setFontWeight(700)
        return text_format

    def highlightBlock(self, text: str) -> None:
        for regex, text_format in self.rules:
            for match in regex.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), text_format)
