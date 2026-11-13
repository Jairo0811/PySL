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
    assert view.file_label.text() == "programa.pysl *"

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


# ---------- converter ----------


def test_swap_converts_the_previous_result_into_the_new_output(qapp: QApplication) -> None:
    from pysl.modules.converter.converter_view import ConverterView

    view = ConverterView()
    view._source.setPlainText('inicio\n    imprimir("Hola")\nfin')
    view._convert()
    python_result = view._target.toPlainText()
    assert 'print("Hola")' in python_result

    view._swap()

    assert view._direction.currentIndex() == 1
    assert view._source.toPlainText() == python_result
    assert "imprimir(" in view._target.toPlainText()
    assert view._target.toPlainText().strip().startswith("inicio")
    assert view._source_label.text() == "Código Python"
    assert view._target_label.text() == "Código SL"


def test_swap_twice_returns_to_an_equivalent_program(qapp: QApplication) -> None:
    from pysl.language import SLExecutor
    from pysl.modules.converter.converter_view import ConverterView

    view = ConverterView()
    original = "inicio\n    entero a = 2\n    imprimir(a * 3)\nfin"
    view._source.setPlainText(original)
    view._convert()
    view._swap()
    view._swap()

    # After two swaps the SL that went SL -> Python -> SL is back in the input panel.
    assert view._direction.currentIndex() == 0
    assert SLExecutor().execute(view._source.toPlainText()).output == "6"


def test_notice_about_the_python_subset_is_only_shown_for_python_to_sl(
    qapp: QApplication,
) -> None:
    from pysl.modules.converter.converter_view import ConverterView

    view = ConverterView()
    view.show()
    assert not view._notice.isVisible()

    view._direction.setCurrentIndex(1)

    assert view._notice.isVisible()
    assert "subconjunto educativo" in view._notice.text()
    view.close()


def test_copy_result_uses_the_clipboard(qapp: QApplication) -> None:
    from pysl.modules.converter.converter_view import ConverterView

    view = ConverterView()
    view._copy_result()

    assert QApplication.clipboard().text() == view._target.toPlainText()
    assert "print" in QApplication.clipboard().text()


def test_failed_conversion_clears_the_stale_result(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch, dialogs: dict
) -> None:
    from pysl.modules.converter.converter_view import ConverterView

    view = ConverterView()
    assert view._target.toPlainText()
    view._source.setPlainText("inicio\n    class = 3\nfin")

    view._convert()

    assert view._target.toPlainText() == ""
    assert dialogs["critical"] == ["Error de conversión"]


# ---------- login ----------


def test_login_identifies_the_demo_account_and_keeps_guest_access(qapp: QApplication) -> None:
    from PySide6.QtWidgets import QLabel, QPushButton

    from pysl.modules.authentication.login_view import LoginView
    from pysl.modules.authentication.service import AuthenticationService

    started: list[str] = []
    view = LoginView(AuthenticationService(), started.append)
    texts = " ".join(label.text() for label in view.findChildren(QLabel))

    assert "Cuenta académica de demostración" in texts
    assert "sesión local" in texts
    assert "Reimagined" not in texts
    guest = next(b for b in view.findChildren(QPushButton) if "invitado" in b.text())
    guest.click()
    assert started == ["Invitado"]


# ---------- games: statistics have one consistent meaning ----------


def _stats(database: Database, key: str) -> tuple[int, int, int]:
    with database.connect() as connection:
        row = connection.execute(
            "SELECT played, won, lost FROM game_stats WHERE game_key = ?", (key,)
        ).fetchone()
    connection.close()
    return (row["played"], row["won"], row["lost"]) if row else (0, 0, 0)


@pytest.mark.parametrize(
    ("moves", "expected"),
    [
        ((0, 3, 1, 4, 2), (1, 1, 0)),  # X wins
        ((0, 3, 1, 4, 8, 5), (1, 0, 1)),  # O wins
        ((0, 1, 2, 4, 3, 5, 7, 6, 8), (1, 0, 0)),  # draw: played only
    ],
)
def test_tic_tac_toe_records_win_loss_and_draw_consistently(
    qapp: QApplication, database: Database, moves: tuple[int, ...], expected: tuple[int, int, int]
) -> None:
    from pysl.modules.games.games_view import TicView

    view = TicView(database)
    for move in moves:
        view.move(move)

    assert _stats(database, "tic_tac_toe") == expected
    assert not any(button.isEnabled() for button in view.buttons)


def test_tic_tac_toe_reset_restores_the_board_without_recording(
    qapp: QApplication, database: Database
) -> None:
    from pysl.modules.games.games_view import TicView

    view = TicView(database)
    view.move(0)
    view.reset()

    assert all(button.text() == " " and button.isEnabled() for button in view.buttons)
    assert view.status.text() == "Turno: X"
    assert _stats(database, "tic_tac_toe") == (0, 0, 0)


def test_rock_paper_scissors_draw_is_not_a_loss(
    qapp: QApplication, database: Database, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pysl.modules.games import games_view

    view = games_view.RpsView(database)
    for user_result in (("ganaste", "tijera"), ("perdiste", "papel"), ("empate", "piedra")):
        monkeypatch.setattr(games_view, "play", lambda _choice, result=user_result: result)
        view.run()

    assert _stats(database, "rps") == (3, 1, 1)


def test_guess_game_counts_only_finished_games_and_restarts(
    qapp: QApplication, database: Database
) -> None:
    from pysl.modules.games.games_view import GuessView
    from pysl.modules.games.guess_number.service import GuessNumberGame

    view = GuessView(database)
    view.game = GuessNumberGame(40)
    view.value.setValue(10)
    view.guess()
    assert "mayor" in view.result.text()
    assert _stats(database, "guess") == (0, 0, 0)

    view.value.setValue(40)
    view.guess()
    assert "Correcto en 2 intentos" in view.result.text()
    assert _stats(database, "guess") == (1, 1, 0)
    assert view.game.attempts == 0
