from pathlib import Path

import pytest

from pysl.core.database import Database


def test_database_persists_progress(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    db.mark_completed("variables")
    db.record_game("guess", True)
    summary = db.summary()
    assert summary.completed_labs == 1
    assert summary.games_played == 1
    assert summary.games_won == 1


def test_preferences(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    db.set_preference("theme", "Oscuro")
    assert db.get_preference("theme") == "Oscuro"


def test_database_validates_keys_and_scores(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")

    with pytest.raises(ValueError, match="item_key"):
        db.mark_completed("")
    with pytest.raises(ValueError, match="score"):
        db.mark_completed("variables", score=101)


def test_database_closes_every_connection(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import sqlite3

    class TrackingConnection(sqlite3.Connection):
        closed = False

        def close(self) -> None:
            self.closed = True
            super().close()

    opened: list[TrackingConnection] = []

    real_connect = sqlite3.connect

    def tracking_connect(*args: object, **kwargs: object) -> sqlite3.Connection:
        connection = real_connect(*args, factory=TrackingConnection, **kwargs)  # type: ignore[arg-type]
        opened.append(connection)  # type: ignore[arg-type]
        return connection

    monkeypatch.setattr("pysl.core.database.sqlite3.connect", tracking_connect)

    db = Database(tmp_path / "test.db")
    db.mark_completed("variables")
    db.record_game("guess", True)
    db.set_preference("theme", "Oscuro")
    db.get_preference("theme")
    db.summary()
    db.reset()

    assert opened
    assert all(connection.closed for connection in opened)


def test_record_game_distinguishes_draws_from_losses(tmp_path: Path) -> None:
    db = Database(tmp_path / "test.db")
    db.record_game("tic_tac_toe", True)
    db.record_game("tic_tac_toe", False)
    db.record_game("tic_tac_toe", False, drawn=True)

    with db.connect() as connection:
        row = connection.execute(
            "SELECT played, won, lost FROM game_stats WHERE game_key = ?", ("tic_tac_toe",)
        ).fetchone()
    assert (row["played"], row["won"], row["lost"]) == (3, 1, 1)

    with pytest.raises(ValueError, match="empate"):
        db.record_game("tic_tac_toe", True, drawn=True)
