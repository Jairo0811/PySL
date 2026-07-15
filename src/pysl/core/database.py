from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from pysl.core.settings import SETTINGS


@dataclass(frozen=True, slots=True)
class ProgressSummary:
    completed_labs: int
    games_played: int
    games_won: int


class Database:
    """Small SQLite persistence layer for progress and preferences."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (SETTINGS.data_dir / "pysl.db")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS progress (
                    item_key TEXT PRIMARY KEY,
                    item_type TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0,
                    score INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS game_stats (
                    game_key TEXT PRIMARY KEY,
                    played INTEGER NOT NULL DEFAULT 0,
                    won INTEGER NOT NULL DEFAULT 0,
                    lost INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS preferences (
                    preference_key TEXT PRIMARY KEY,
                    preference_value TEXT NOT NULL
                );
                """
            )

    def mark_completed(self, item_key: str, item_type: str = "lab", score: int = 100) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO progress(item_key, item_type, completed, score)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(item_key) DO UPDATE SET
                    completed = 1, score = excluded.score, updated_at = CURRENT_TIMESTAMP
                """,
                (item_key, item_type, score),
            )

    def record_game(self, game_key: str, won: bool) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO game_stats(game_key, played, won, lost)
                VALUES (?, 1, ?, ?)
                ON CONFLICT(game_key) DO UPDATE SET
                    played = played + 1,
                    won = won + excluded.won,
                    lost = lost + excluded.lost
                """,
                (game_key, int(won), int(not won)),
            )

    def summary(self) -> ProgressSummary:
        with self.connect() as connection:
            completed = connection.execute(
                "SELECT COUNT(*) FROM progress WHERE completed = 1"
            ).fetchone()[0]
            row = connection.execute(
                "SELECT COALESCE(SUM(played),0), COALESCE(SUM(won),0) FROM game_stats"
            ).fetchone()
        return ProgressSummary(completed, row[0], row[1])

    def set_preference(self, key: str, value: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO preferences VALUES (?, ?) ON CONFLICT(preference_key) DO UPDATE SET preference_value=excluded.preference_value",
                (key, value),
            )

    def get_preference(self, key: str, default: str = "") -> str:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT preference_value FROM preferences WHERE preference_key = ?", (key,)
            ).fetchone()
        return row[0] if row else default

    def reset(self) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM progress")
            connection.execute("DELETE FROM game_stats")
            connection.execute("DELETE FROM preferences")
