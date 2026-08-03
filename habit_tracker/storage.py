"""SQLite persistence. Two tables, tiny API."""
import sqlite3
from datetime import datetime
from pathlib import Path

from .habit import Habit

DEFAULT_DB = Path.home() / ".habit_tracker.db"


class Storage:
    """Wraps a SQLite connection. Use as a context manager."""

    def __init__(self, path=DEFAULT_DB):
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS habits (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                name         TEXT NOT NULL UNIQUE,
                description  TEXT NOT NULL,
                periodicity  TEXT NOT NULL,
                created_at   TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS completions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id     INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
            );
        """)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.conn.close()

    def add(self, habit):
        """Persist a habit (and any completions it already has)."""
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO habits(name, description, periodicity, created_at) "
                "VALUES (?,?,?,?)",
                (habit.name, habit.description, habit.periodicity,
                 habit.created_at.isoformat()),
            )
            habit.habit_id = cur.lastrowid
            if habit.completions:
                self.conn.executemany(
                    "INSERT INTO completions(habit_id, completed_at) VALUES (?,?)",
                    [(habit.habit_id, c.isoformat()) for c in habit.completions],
                )
        return habit

    def delete(self, name):
        """Delete by name. Returns True if a row was removed."""
        with self.conn:
            return self.conn.execute(
                "DELETE FROM habits WHERE name = ?", (name,)
            ).rowcount > 0

    def get(self, name):
        """Load one habit (with its completions). None if not found."""
        row = self.conn.execute(
            "SELECT id, name, description, periodicity, created_at "
            "FROM habits WHERE name = ?",
            (name,),
        ).fetchone()
        return self._row_to_habit(row) if row else None

    def all(self):
        """Load every habit."""
        rows = self.conn.execute(
            "SELECT id, name, description, periodicity, created_at "
            "FROM habits ORDER BY id"
        ).fetchall()
        return [self._row_to_habit(r) for r in rows]

    def check_off(self, name, when=None):
        """Record a completion. Raises KeyError if the habit is unknown."""
        habit = self.get(name)
        if habit is None:
            raise KeyError(f"No habit named {name!r}")
        ts = when or datetime.now()
        with self.conn:
            self.conn.execute(
                "INSERT INTO completions(habit_id, completed_at) VALUES (?,?)",
                (habit.habit_id, ts.isoformat()),
            )
        return ts

    def seed(self, habits):
        """Insert habits that don't already exist. Idempotent."""
        existing = {h.name for h in self.all()}
        for h in habits:
            if h.name not in existing:
                self.add(h)

    def _row_to_habit(self, row):
        habit_id, name, description, periodicity, created_at = row
        completions = [
            datetime.fromisoformat(r[0])
            for r in self.conn.execute(
                "SELECT completed_at FROM completions WHERE habit_id = ? "
                "ORDER BY completed_at",
                (habit_id,),
            )
        ]
        return Habit(
            name=name,
            description=description,
            periodicity=periodicity,
            created_at=datetime.fromisoformat(created_at),
            completions=completions,
            habit_id=habit_id,
        )

