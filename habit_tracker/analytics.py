"""Analytics – all functions here are pure and stateless.

Each function takes an iterable of Habit objects and returns a fresh
value. No I/O, no globals, no mutation – that's the "functional
programming" part of the assignment.
"""
from datetime import datetime
from functools import reduce

from .habit import _period_key, _step


def all_habits(habits):
    return list(habits)


def by_period(habits, periodicity):
    return list(filter(lambda h: h.periodicity == periodicity, habits))


def longest_streak(habits):
    """Longest streak across every habit (0 if there are none)."""
    return reduce(max, map(lambda h: h.longest_streak(), habits), 0)


def longest_streak_of(habits, name):
    """Longest streak of a specific habit. Raises KeyError if not found."""
    for h in habits:
        if h.name == name:
            return h.longest_streak()
    raise KeyError(name)


def top_streak_habit(habits):
    """The habit that holds the record. None if there are no habits."""
    habits = list(habits)
    if not habits:
        return None
    return reduce(
        lambda best, h: h if h.longest_streak() > best.longest_streak() else best,
        habits,
    )


def broken(habits, now=None):
    now = now or datetime.now()
    return list(filter(lambda h: h.is_broken(now), habits))


def struggled_since(habits, since, now=None):
    """(habit, misses) pairs sorted by misses descending.

    Only counts full periods inside [since, now]. Habits with zero
    misses are dropped from the result.
    """
    now = now or datetime.now()

    def misses(h):
        start = _period_key(since, h.periodicity)
        end = _period_key(now, h.periodicity)
        done = {_period_key(c, h.periodicity) for c in h.completions}
        count, k = 0, start
        while k <= end:
            if k not in done:
                count += 1
            k = _step(k, h.periodicity)
        return count

    scored = ((h, misses(h)) for h in habits)
    return sorted((p for p in scored if p[1] > 0),
                  key=lambda p: p[1], reverse=True)


def summary(habits):
    """One dict per habit – handy for printing or JSON export."""
    return list(map(lambda h: {
        "name": h.name,
        "periodicity": h.periodicity,
        "completions": len(h.completions),
        "longest_streak": h.longest_streak(),
        "current_streak": h.current_streak(),
        "broken": h.is_broken(),
    }, habits))

