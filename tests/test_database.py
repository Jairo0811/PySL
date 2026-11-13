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


def test_corrupt_database_is_quarantined_and_recreated(tmp_path: Path) -> None:
    path = tmp_path / "pysl.db"
    path.write_bytes(b"esto no es una base sqlite" * 50)

    db = Database(path)
    db.record_game("hangman", True)

    assert db.summary().games_played == 1
    backups = list(tmp_path.glob("pysl.db.corrupt-*"))
    assert len(backups) == 1
    assert backups[0].read_bytes().startswith(b"esto no es")


def test_new_database_records_schema_version_and_uses_wal(tmp_path: Path) -> None:
    db = Database(tmp_path / "nuevo.db")

    with db.connect() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
        assert connection.execute("PRAGMA busy_timeout").fetchone()[0] == 5000
    connection.close()


def test_reopening_keeps_data_and_missing_directories_are_created(tmp_path: Path) -> None:
    path = tmp_path / "a" / "b" / "pysl.db"
    Database(path).mark_completed("smallest_even")

    assert Database(path).summary().completed_labs == 1


def test_reset_clears_every_table(tmp_path: Path) -> None:
    db = Database(tmp_path / "t.db")
    db.mark_completed("x")
    db.record_game("g", True)
    db.set_preference("theme", "Claro")

    db.reset()

    assert db.summary().completed_labs == 0
    assert db.summary().games_played == 0
    assert db.get_preference("theme", "Oscuro") == "Oscuro"
