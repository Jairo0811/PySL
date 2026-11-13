from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from pysl.core.database import Database
from pysl.modules.editor.editor_view import SAMPLE, EditorView
from pysl.modules.exercises.smallest_even.view import SmallestEvenView
from pysl.modules.home.home_view import HomeView
from pysl.modules.settings.settings_view import SettingsView
from pysl.ui.main_window import MainWindow
from pysl.ui.styles import DARK_THEME, LIGHT_THEME, apply_theme

Button = QMessageBox.StandardButton


@pytest.fixture
def database(tmp_path: Path) -> Database:
    return Database(tmp_path / "views.db")


@pytest.fixture
def dialogs(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    """Replace blocking message boxes with recorders so tests never wait for a click."""
    calls: dict[str, list[str]] = {"critical": [], "question": []}
    monkeypatch.setattr(
        QMessageBox, "critical", lambda _parent, title, _text: calls["critical"].append(title)
    )
    return calls


def _answer_question(monkeypatch: pytest.MonkeyPatch, button: Button) -> list[str]:
    asked: list[str] = []

    def question(_parent: object, title: str, *_args: object) -> Button:
        asked.append(title)
        return button

    monkeypatch.setattr(QMessageBox, "question", question)
    return asked


def _wait_for_execution(application: QApplication) -> None:
    QThreadPool.globalInstance().waitForDone(20_000)
    application.processEvents()


# ---------- editor ----------


def test_failed_open_does_not_change_the_current_file(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, dialogs: dict
) -> None:
    previous = tmp_path / "previous.pysl"
    previous.write_text("inicio\nfin", encoding="utf-8")
    broken = tmp_path / "broken.pysl"
    broken.write_bytes(b"\xff\xfe\xfa not utf-8")
    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *_a, **_k: (str(broken), ""))

    view = EditorView()
    view.current_path = previous
    view._open()

    assert view.current_path == previous
    assert dialogs["critical"] == ["No se pudo abrir el archivo"]
    assert previous.read_text(encoding="utf-8") == "inicio\nfin"


def test_unsaved_changes_are_protected_before_discarding(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    view = EditorView()
    view.editor.setPlainText("inicio\nimprimir(1)\nfin")
    view.editor.document().setModified(True)

    asked = _answer_question(monkeypatch, Button.Cancel)
    view._new()
    assert view.editor.toPlainText().startswith("inicio\nimprimir(1)")
    assert asked == ["Cambios sin guardar"]

    _answer_question(monkeypatch, Button.Discard)
    view._new()
    assert view.editor.toPlainText() == SAMPLE
    assert not view.editor.document().isModified()


def test_clean_editor_never_prompts(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> None:
    asked = _answer_question(monkeypatch, Button.Cancel)
    view = EditorView()

    assert view.confirm_discard()
    assert asked == []


def test_save_clears_the_modified_marker(qapp: QApplication, tmp_path: Path) -> None:
    target = tmp_path / "programa.pysl"
    view = EditorView()
    view.current_path = target
    view.editor.setPlainText("inicio\nfin")
    view.editor.document().setModified(True)
    view._update_file_label()
    assert view.file_label.text() == "programa.pysl ●"

    assert view._save() is True

    assert target.read_text(encoding="utf-8") == "inicio\nfin"
    assert view.file_label.text() == "programa.pysl"


def test_failed_save_as_restores_the_previous_path(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, dialogs: dict
) -> None:
    missing_folder = tmp_path / "no-existe" / "nuevo"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *_a, **_k: (str(missing_folder), ""))
    view = EditorView()
    original = tmp_path / "original.pysl"
    view.current_path = original

    assert view._save_as() is False

    assert view.current_path == original
    assert dialogs["critical"] == ["No se pudo guardar el archivo"]


def test_runtime_error_highlights_the_failing_line_and_clears_on_edit(
    qapp: QApplication,
) -> None:
    view = EditorView()
    view.editor.setPlainText("inicio\nentero a = 1\nentero b = a / 0\nfin")

    view._run()
    _wait_for_execution(qapp)

    assert "división entre cero" in view.console.toPlainText()
    assert "(línea 3)" in view.console.toPlainText()
    assert view.editor.error_line == 3
    assert len(view.editor.extraSelections()) == 2
    assert view.editor.textCursor().blockNumber() == 2

    view.editor.appendPlainText("// edición")
    assert view.editor.error_line is None
    assert len(view.editor.extraSelections()) == 1


def test_syntax_error_highlights_its_line(qapp: QApplication) -> None:
    view = EditorView()
    view.editor.setPlainText("inicio\nimprimir(1)\nclass = 3\nfin")

    view._run()
    _wait_for_execution(qapp)

    assert "palabra reservada" in view.console.toPlainText()
    assert view.editor.error_line == 3


def test_successful_run_clears_a_previous_error(qapp: QApplication) -> None:
    view = EditorView()
    view.editor.setPlainText("inicio\nentero a = 1 / 0\nfin")
    view._run()
    _wait_for_execution(qapp)
    assert view.editor.error_line == 2

    view.editor.setPlainText('inicio\nimprimir("ok")\nfin')
    view._run()
    _wait_for_execution(qapp)

    assert view.editor.error_line is None
    assert view.console.toPlainText() == "ok"


# ---------- home / lab progress ----------


def test_home_statistics_refresh_when_shown(qapp: QApplication, database: Database) -> None:
    view = HomeView("Ana", lambda _name: None, database)
    assert view._stat_values["played"].text() == "0"

    database.record_game("hangman", True)
    database.record_game("hangman", False)
    database.mark_completed("smallest_even")
    view.show()

    assert view._stat_values["played"].text() == "2"
    assert view._stat_values["won"].text() == "1"
    assert view._stat_values["labs"].text() == "1"
    view.close()


def test_solving_the_lab_records_progress(
    qapp: QApplication, database: Database, monkeypatch: pytest.MonkeyPatch
) -> None:
    warnings: list[str] = []
    monkeypatch.setattr(QMessageBox, "warning", lambda _p, title, _t: warnings.append(title))
    view = SmallestEvenView(database)

    for field, value in zip(view._inputs, ("7", "x", "3", "9", "1"), strict=True):
        field.setText(value)
    view._solve()
    assert warnings == ["Datos inválidos"]
    assert database.summary().completed_labs == 0

    for field, value in zip(view._inputs, ("7", "8", "3", "4", "1"), strict=True):
        field.setText(value)
    view._solve()
    assert database.summary().completed_labs == 1


# ---------- settings ----------


def test_unsaved_theme_preview_is_reverted_when_leaving_the_page(
    qapp: QApplication, database: Database
) -> None:
    apply_theme(qapp, DARK_THEME, 14)
    view = SettingsView(database)
    view.show()

    view.theme.setCurrentText(LIGHT_THEME)
    view.font_size.setValue(20)
    assert qapp.property("pysl_theme") == LIGHT_THEME

    view.hide()

    assert view.theme.currentText() == DARK_THEME
    assert view.font_size.value() == 14
    assert qapp.property("pysl_theme") == DARK_THEME
    assert qapp.property("pysl_font_size") == 14


def test_saved_theme_survives_leaving_the_page(
    qapp: QApplication, database: Database, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(QMessageBox, "information", lambda *_a, **_k: None)
    apply_theme(qapp, DARK_THEME, 14)
    view = SettingsView(database)
    view.show()

    view.theme.setCurrentText(LIGHT_THEME)
    view._save()
    view.hide()

    assert qapp.property("pysl_theme") == LIGHT_THEME
    assert database.get_preference("theme") == LIGHT_THEME
    apply_theme(qapp, DARK_THEME, 14)


def test_corrupt_font_preference_falls_back_to_default(
    qapp: QApplication, database: Database
) -> None:
    database.set_preference("font_size", "enorme")

    assert SettingsView(database).font_size.value() == 14


# ---------- application shell ----------


def test_closing_the_app_asks_before_discarding_editor_changes(
    qapp: QApplication, database: Database, monkeypatch: pytest.MonkeyPatch
) -> None:
    window = MainWindow(database)
    window.show()
    window._handle_authenticated("Ana")
    dashboard = window._stack.currentWidget()
    dashboard._editor_view.editor.appendPlainText("// cambio sin guardar")

    asked = _answer_question(monkeypatch, Button.Cancel)
    assert window.close() is False
    assert asked == ["Cambios sin guardar"]

    _answer_question(monkeypatch, Button.Discard)
    assert window.close() is True


def test_logout_is_blocked_while_the_user_cancels_the_prompt(
    qapp: QApplication, database: Database, monkeypatch: pytest.MonkeyPatch
) -> None:
    window = MainWindow(database)
    window._handle_authenticated("Ana")
    dashboard = window._stack.currentWidget()
    dashboard._editor_view.editor.appendPlainText("// cambio sin guardar")

    _answer_question(monkeypatch, Button.Cancel)
    window._handle_logout()

    assert window._stack.currentWidget() is dashboard
