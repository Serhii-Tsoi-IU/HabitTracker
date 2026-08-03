"""CRUD round-trip and persistence across sessions."""
from datetime import datetime

from habit_tracker.habit import DAILY, Habit
from habit_tracker.storage import Storage


def test_crud_roundtrip_persists_across_sessions(tmp_path):
    db = tmp_path / "s.db"

    # write in one session...
    with Storage(db) as store:
        store.add(Habit("read", "read a book", DAILY,
                        completions=[datetime(2026, 4, 1, 20)]))
        store.check_off("read", datetime(2026, 4, 2, 20))

    # ...read back in another
    with Storage(db) as store:
        loaded = store.get("read")
        assert loaded.periodicity == DAILY
        assert loaded.completions == [datetime(2026, 4, 1, 20),
                                       datetime(2026, 4, 2, 20)]
        assert store.delete("read") is True
        assert store.get("read") is None


def test_seed_is_idempotent(store):
    from habit_tracker.fixtures import predefined_habits
    store.seed(predefined_habits())          # second seed is a no-op
    assert len(store.all()) == 5

