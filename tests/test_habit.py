"""The essentials: streak counting on real fixture data, plus is_broken."""
from datetime import datetime

import pytest

from habit_tracker.fixtures import FIXTURE_NOW
from habit_tracker.habit import DAILY, Habit


def _get(habits, name):
    return next(h for h in habits if h.name == name)


def test_periodicity_is_validated():
    with pytest.raises(ValueError):
        Habit("x", "y", "hourly")


def test_complete_records_a_timestamp():
    h = Habit("x", "y", DAILY)
    ts = datetime(2026, 1, 1, 12)
    h.complete(ts)
    assert h.completions == [ts]


def test_longest_streak_across_daily_and_weekly(habits):
    # 28 completed days -> streak 28
    assert _get(habits, "brush_teeth").longest_streak() == 28
    # 28 days minus indices 7 and 14 -> best segment is 13
    assert _get(habits, "read_book").longest_streak() == 13
    # 4 completed weeks in a row
    assert _get(habits, "exercise").longest_streak() == 4


def test_is_broken_reflects_the_last_period(habits):
    # brush_teeth completed through yesterday -> not broken
    assert _get(habits, "brush_teeth").is_broken(FIXTURE_NOW) is False
    # clean_room missed several weeks -> broken
    assert _get(habits, "clean_room").is_broken(FIXTURE_NOW) is True

