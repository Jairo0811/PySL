import re
from typing import Any

from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat
from PySide6.QtWidgets import QApplication

from pysl.ui.styles import DARK_THEME, LIGHT_THEME, normalize_theme


class SLHighlighter(QSyntaxHighlighter):
    """Highlight the supported SL 1.0 syntax using theme-aware colors."""

    def __init__(self, document: Any) -> None:
        super().__init__(document)
        self.rules: list[tuple[re.Pattern[str], QTextCharFormat]] = []
        self.refresh_theme()

    def refresh_theme(self) -> None:
        theme = self._active_theme()
        if theme == LIGHT_THEME:
            keyword = self._format("#6d28d9", bold=True)
            builtin = self._format("#1d4ed8")
            string = self._format("#92400e")
            comment = self._format("#64748b")
        else:
            keyword = self._format("#c084fc", bold=True)
            builtin = self._format("#60a5fa")
            string = self._format("#fbbf24")
            comment = self._format("#94a3b8")

        self.rules.clear()
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
        self.rehighlight()

    @staticmethod
    def _format(color: str, *, bold: bool = False) -> QTextCharFormat:
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        if bold:
            text_format.setFontWeight(700)
        return text_format

    @staticmethod
    def _active_theme() -> str:
        application = QApplication.instance()
        if application is None:
            return DARK_THEME
        theme = application.property("pysl_theme")
        return normalize_theme(str(theme) if theme else DARK_THEME)

    def highlightBlock(self, text: str) -> None:
        for regex, text_format in self.rules:
            for match in regex.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), text_format)
