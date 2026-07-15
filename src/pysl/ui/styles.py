APP_STYLESHEET = """
QWidget {
    background-color: #0b1220;
    color: #f8fafc;
    font-family: "Segoe UI";
    font-size: 14px;
}
QFrame#sidebar, QFrame#card, QFrame#statCard {
    background-color: #151f30;
    border: 1px solid #263449;
    border-radius: 16px;
}
QFrame#sidebar { border-radius: 18px; }
QLabel#title { font-size: 30px; font-weight: 750; }
QLabel#pageTitle { font-size: 28px; font-weight: 750; }
QLabel#sectionTitle { font-size: 19px; font-weight: 700; }
QLabel#subtitle, QLabel#muted { color: #94a3b8; }
QLabel#accent { color: #a78bfa; font-weight: 700; }
QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 10px;
    selection-background-color: #7c3aed;
}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #8b5cf6;
}
QPushButton {
    background-color: #7c3aed;
    border: none;
    border-radius: 10px;
    padding: 11px 16px;
    font-weight: 650;
}
QPushButton:hover { background-color: #8b5cf6; }
QPushButton:pressed { background-color: #6d28d9; }
QPushButton#secondaryButton { background-color: #334155; }
QPushButton#secondaryButton:hover { background-color: #475569; }
QPushButton#dangerButton { background-color: #991b1b; }
QPushButton#dangerButton:hover { background-color: #b91c1c; }
QPushButton#successButton { background-color: #047857; }
QGroupBox {
    border: 1px solid #334155;
    border-radius: 12px;
    margin-top: 12px;
    padding: 16px 10px 10px 10px;
    font-weight: 650;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
QTableWidget, QTabWidget::pane {
    background-color: #151f30;
    border: 1px solid #334155;
    border-radius: 10px;
}
QHeaderView::section {
    background-color: #334155;
    color: #f8fafc;
    padding: 8px;
    border: none;
}
QLabel#resultLabel {
    background-color: #151f30;
    border-left: 4px solid #8b5cf6;
    border-radius: 8px;
    padding: 12px;
    font-weight: 650;
}
QPlainTextEdit#codeEditor, QPlainTextEdit#console {
    font-family: Consolas, "Cascadia Code";
    font-size: 14px;
}
QListWidget {
    background-color: transparent;
    border: none;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 13px 12px;
    margin: 2px 0;
    border-radius: 9px;
}
QListWidget::item:hover { background-color: #263449; }
QListWidget::item:selected { background-color: #7c3aed; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #0f172a; width: 10px; }
QScrollBar::handle:vertical { background: #475569; border-radius: 5px; }
QTabBar::tab { background: #151f30; padding: 10px 14px; }
QTabBar::tab:selected { background: #7c3aed; }
"""
