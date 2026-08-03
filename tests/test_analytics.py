"""The four required analytics queries + broken-habits helper."""
from habit_tracker import analytics
from habit_tracker.fixtures import FIXTURE_NOW
from habit_tracker.habit import DAILY, WEEKLY


def test_listings(habits):
    assert len(analytics.all_habits(habits)) == 5
    assert {h.name for h in analytics.by_period(habits, DAILY)} == {
        "brush_teeth", "drink_water", "read_book",
    }
    assert {h.name for h in analytics.by_period(habits, WEEKLY)} == {
        "exercise", "clean_room",
    }


def test_longest_streak_overall_and_per_habit(habits):
    assert analytics.longest_streak(habits) == 28
    assert analytics.longest_streak_of(habits, "read_book") == 13
    assert analytics.top_streak_habit(habits).name in {"brush_teeth", "drink_water"}


def test_broken_finds_missed_habits(habits):
    names = {h.name for h in analytics.broken(habits, FIXTURE_NOW)}
    assert "clean_room" in names
    assert "brush_teeth" not in names

