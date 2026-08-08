from __future__ import annotations

from typing import Final

from PySide6.QtWidgets import QApplication

DARK_THEME: Final = "Oscuro"
LIGHT_THEME: Final = "Claro"
DEFAULT_FONT_SIZE: Final = 14

_THEME_COLORS: Final = {
    DARK_THEME: {
        "background": "#0b1220",
        "foreground": "#f8fafc",
        "card": "#151f30",
        "border": "#263449",
        "input": "#0f172a",
        "muted": "#94a3b8",
        "accent": "#a78bfa",
        "primary": "#7c3aed",
        "primary_hover": "#8b5cf6",
        "primary_pressed": "#6d28d9",
        "secondary": "#334155",
        "secondary_hover": "#475569",
        "danger": "#991b1b",
        "danger_hover": "#b91c1c",
        "success": "#047857",
        "header": "#334155",
        "scrollbar": "#0f172a",
        "scroll_handle": "#475569",
        "line_number_background": "#111827",
        "line_number_foreground": "#64748b",
        "current_line": "#172033",
    },
    LIGHT_THEME: {
        "background": "#f8fafc",
        "foreground": "#0f172a",
        "card": "#ffffff",
        "border": "#cbd5e1",
        "input": "#ffffff",
        "muted": "#64748b",
        "accent": "#6d28d9",
        "primary": "#7c3aed",
        "primary_hover": "#6d28d9",
        "primary_pressed": "#5b21b6",
        "secondary": "#e2e8f0",
        "secondary_hover": "#cbd5e1",
        "danger": "#b91c1c",
        "danger_hover": "#991b1b",
        "success": "#047857",
        "header": "#e2e8f0",
        "scrollbar": "#e2e8f0",
        "scroll_handle": "#94a3b8",
        "line_number_background": "#f1f5f9",
        "line_number_foreground": "#64748b",
        "current_line": "#ede9fe",
    },
}


def normalize_theme(theme: str) -> str:
    """Return a supported theme name, falling back to the dark theme."""
    return LIGHT_THEME if theme.strip().casefold() == LIGHT_THEME.casefold() else DARK_THEME


def normalize_font_size(font_size: int) -> int:
    """Keep the configurable UI/editor font size inside the supported range."""
    return max(11, min(24, int(font_size)))


def theme_colors(theme: str) -> dict[str, str]:
    """Expose a copy of the active color tokens for custom-painted widgets."""
    return dict(_THEME_COLORS[normalize_theme(theme)])


def get_stylesheet(theme: str = DARK_THEME, font_size: int = DEFAULT_FONT_SIZE) -> str:
    """Build the application stylesheet for the selected theme and font size."""
    colors = _THEME_COLORS[normalize_theme(theme)]
    size = normalize_font_size(font_size)

    return f"""
QWidget {{
    background-color: {colors["background"]};
    color: {colors["foreground"]};
    font-family: "Segoe UI";
    font-size: {size}px;
}}
QFrame#sidebar, QFrame#card, QFrame#statCard {{
    background-color: {colors["card"]};
    border: 1px solid {colors["border"]};
    border-radius: 16px;
}}
QFrame#sidebar {{ border-radius: 18px; }}
QLabel#title {{ font-size: 30px; font-weight: 750; }}
QLabel#pageTitle {{ font-size: 28px; font-weight: 750; }}
QLabel#sectionTitle {{ font-size: 19px; font-weight: 700; }}
QLabel#subtitle, QLabel#muted {{ color: {colors["muted"]}; }}
QLabel#accent {{ color: {colors["accent"]}; font-weight: 700; }}
QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox {{
    background-color: {colors["input"]};
    color: {colors["foreground"]};
    border: 1px solid {colors["border"]};
    border-radius: 10px;
    padding: 10px;
    selection-background-color: {colors["primary"]};
}}
QComboBox QAbstractItemView {{
    background-color: {colors["card"]};
    color: {colors["foreground"]};
    selection-background-color: {colors["primary"]};
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus {{
    border: 1px solid {colors["primary_hover"]};
}}
QPushButton {{
    background-color: {colors["primary"]};
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 11px 16px;
    font-weight: 650;
}}
QPushButton:hover {{ background-color: {colors["primary_hover"]}; }}
QPushButton:pressed {{ background-color: {colors["primary_pressed"]}; }}
QPushButton#secondaryButton {{
    background-color: {colors["secondary"]};
    color: {colors["foreground"]};
}}
QPushButton#secondaryButton:hover {{ background-color: {colors["secondary_hover"]}; }}
QPushButton#dangerButton {{ background-color: {colors["danger"]}; color: #ffffff; }}
QPushButton#dangerButton:hover {{ background-color: {colors["danger_hover"]}; }}
QPushButton#successButton {{ background-color: {colors["success"]}; color: #ffffff; }}
QGroupBox {{
    border: 1px solid {colors["border"]};
    border-radius: 12px;
    margin-top: 12px;
    padding: 16px 10px 10px 10px;
    font-weight: 650;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 5px; }}
QTableWidget, QTabWidget::pane {{
    background-color: {colors["card"]};
    color: {colors["foreground"]};
    border: 1px solid {colors["border"]};
    border-radius: 10px;
}}
QHeaderView::section {{
    background-color: {colors["header"]};
    color: {colors["foreground"]};
    padding: 8px;
    border: none;
}}
QLabel#resultLabel {{
    background-color: {colors["card"]};
    border-left: 4px solid {colors["primary_hover"]};
    border-radius: 8px;
    padding: 12px;
    font-weight: 650;
}}
QPlainTextEdit#codeEditor, QPlainTextEdit#console {{
    font-family: Consolas, "Cascadia Code";
    font-size: {size}px;
}}
QListWidget {{
    background-color: transparent;
    color: {colors["foreground"]};
    border: none;
    padding: 4px;
    outline: none;
}}
QListWidget::item {{
    padding: 13px 12px;
    margin: 2px 0;
    border-radius: 9px;
}}
QListWidget::item:hover {{ background-color: {colors["secondary"]}; }}
QListWidget::item:selected {{ background-color: {colors["primary"]}; color: #ffffff; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: {colors["scrollbar"]}; width: 10px; }}
QScrollBar::handle:vertical {{ background: {colors["scroll_handle"]}; border-radius: 5px; }}
QTabBar::tab {{
    background: {colors["card"]};
    color: {colors["foreground"]};
    padding: 10px 14px;
}}
QTabBar::tab:selected {{ background: {colors["primary"]}; color: #ffffff; }}
QToolTip {{
    background-color: {colors["card"]};
    color: {colors["foreground"]};
    border: 1px solid {colors["border"]};
}}
"""


def apply_theme(
    application: QApplication,
    theme: str = DARK_THEME,
    font_size: int = DEFAULT_FONT_SIZE,
) -> None:
    """Apply and broadcast the visual preferences to the running application."""
    normalized_theme = normalize_theme(theme)
    normalized_size = normalize_font_size(font_size)
    application.setProperty("pysl_theme", normalized_theme)
    application.setProperty("pysl_font_size", normalized_size)
    application.setStyleSheet(get_stylesheet(normalized_theme, normalized_size))

    for widget in application.allWidgets():
        refresh_theme = getattr(widget, "refresh_theme", None)
        if callable(refresh_theme):
            refresh_theme()
        widget.update()


APP_STYLESHEET = get_stylesheet()
