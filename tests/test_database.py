from pathlib import Path
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
