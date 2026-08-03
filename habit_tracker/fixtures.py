"""Five predefined habits with four weeks of tracking data.

Everything is anchored to a fixed date (FIXTURE_NOW) so streak numbers
are reproducible – handy for tests and for demoing the CLI.
"""
from datetime import datetime, timedelta

from .habit import DAILY, WEEKLY, Habit

FIXTURE_NOW = datetime(2026, 7, 27, 8, 0)          # a Monday
FIXTURE_START = FIXTURE_NOW - timedelta(days=28)   # 4 weeks earlier, also Monday


def _days(start, n, hour=9):
    return [(start + timedelta(days=i)).replace(hour=hour, minute=0,
                                                second=0, microsecond=0)
            for i in range(n)]


def _weeks(start, n, hour=10):
    return [(start + timedelta(weeks=i)).replace(hour=hour, minute=0,
                                                 second=0, microsecond=0)
            for i in range(n)]


def predefined_habits():
    all_days = _days(FIXTURE_START, 28, hour=20)

    return [
        # daily, perfect record
        Habit("brush_teeth", "Brush your teeth every morning.", DAILY,
              created_at=FIXTURE_START,
              completions=_days(FIXTURE_START, 28, hour=7)),

        # daily, perfect record
        Habit("drink_water", "Drink at least 2 litres of water.", DAILY,
              created_at=FIXTURE_START,
              completions=_days(FIXTURE_START, 28, hour=12)),

        # daily, two gaps (day 8 and day 15) -> longest run drops to 13
        Habit("read_book", "Read at least 20 pages of a book.", DAILY,
              created_at=FIXTURE_START,
              completions=[d for i, d in enumerate(all_days)
                           if i not in (7, 14)]),

        # weekly, all four weeks
        Habit("exercise", "Full workout at least once this week.", WEEKLY,
              created_at=FIXTURE_START,
              completions=_weeks(FIXTURE_START + timedelta(days=2), 4, hour=18)),

        # weekly, only weeks 1 and 3
        Habit("clean_room", "Tidy the whole room.", WEEKLY,
              created_at=FIXTURE_START,
              completions=[w for i, w in enumerate(
                  _weeks(FIXTURE_START + timedelta(days=5), 4))
                  if i in (0, 2)]),
    ]

