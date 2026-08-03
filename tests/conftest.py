import pytest

from habit_tracker.fixtures import predefined_habits
from habit_tracker.storage import Storage


@pytest.fixture
def habits():
    """Fresh copy of the five predefined habits."""
    return predefined_habits()


@pytest.fixture
def store(tmp_path):
    """Storage backed by a temp SQLite file, pre-seeded."""
    with Storage(tmp_path / "test.db") as s:
        s.seed(predefined_habits())
        yield s

