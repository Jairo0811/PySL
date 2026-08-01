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

    _MAX_KEY_LENGTH = 128
    _MAX_PREFERENCE_LENGTH = 4_096

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (SETTINGS.data_dir / "pysl.db")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection

    def _initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode = WAL;
                PRAGMA synchronous = NORMAL;
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
        self._validate_key(item_key, "item_key")
        self._validate_key(item_type, "item_type")
        if not 0 <= score <= 100:
            raise ValueError("score debe estar entre 0 y 100.")
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
        self._validate_key(game_key, "game_key")
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
        return ProgressSummary(int(completed), int(row[0]), int(row[1]))

    def set_preference(self, key: str, value: str) -> None:
        self._validate_key(key, "preference_key")
        if len(value) > self._MAX_PREFERENCE_LENGTH:
            raise ValueError("La preferencia supera el tamaño máximo permitido.")
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO preferences(preference_key, preference_value)
                VALUES (?, ?)
                ON CONFLICT(preference_key) DO UPDATE SET
                    preference_value = excluded.preference_value
                """,
                (key, value),
            )

    def get_preference(self, key: str, default: str = "") -> str:
        self._validate_key(key, "preference_key")
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

    @classmethod
    def _validate_key(cls, value: str, field_name: str) -> None:
        if not value or len(value) > cls._MAX_KEY_LENGTH or "\x00" in value:
            raise ValueError(f"{field_name} no es válido.")
