"""The Habit class – one file, no ceremony.

A habit has a name, a description, a periodicity ("daily" or "weekly"),
a creation timestamp, and a list of completion timestamps.

The interesting bit is streak counting. A "period" is either a single
calendar day or a single ISO week. If the habit was checked off at least
once in that period, the period counts. Consecutive completed periods
form a streak.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

DAILY = "daily"
WEEKLY = "weekly"
PERIODS = (DAILY, WEEKLY)


def _period_key(when, periodicity):
    """Reduce a timestamp to a single integer identifying its period.

    For daily habits it's just the day's ordinal number.
    For weekly habits it's the ordinal of the Monday of that ISO week –
    that way "one week later" is simply +7, no calendar acrobatics.
    """
    d = when.date() if isinstance(when, datetime) else when
    if periodicity == DAILY:
        return d.toordinal()
    monday = d - timedelta(days=d.weekday())
    return monday.toordinal()


def _step(key, periodicity):
    return key + (1 if periodicity == DAILY else 7)


@dataclass
class Habit:
    name: str
    description: str
    periodicity: str                       # "daily" or "weekly"
    created_at: datetime = field(default_factory=datetime.now)
    completions: list = field(default_factory=list)
    habit_id: int | None = None            # set by Storage after insert

    def __post_init__(self):
        if self.periodicity not in PERIODS:
            raise ValueError(
                f"periodicity must be one of {PERIODS}, got {self.periodicity!r}"
            )

    def complete(self, when=None):
        """Check the habit off. Returns the timestamp that was stored."""
        ts = when or datetime.now()
        self.completions.append(ts)
        self.completions.sort()
        return ts

    def _completed_periods(self):
        seen = set()
        result = []
        for c in sorted(self.completions):
            k = _period_key(c, self.periodicity)
            if k not in seen:
                seen.add(k)
                result.append(k)
        return result

    def longest_streak(self):
        """Longest run of consecutive completed periods, ever."""
        keys = self._completed_periods()
        if not keys:
            return 0
        best = run = 1
        for a, b in zip(keys, keys[1:]):
            run = run + 1 if _step(a, self.periodicity) == b else 1
            best = max(best, run)
        return best

    def current_streak(self, now=None):
        """Streak counted backwards from *now*.

        The current period counts if it has already been checked off;
        otherwise the streak counts back from the immediately preceding
        period. If the last completion is older than that, we're broken
        and the streak is 0.
        """
        now = now or datetime.now()
        keys = self._completed_periods()
        if not keys:
            return 0

        today = _period_key(now, self.periodicity)
        last = keys[-1]

        if last == today:
            anchor = today
        elif _step(last, self.periodicity) == today:
            anchor = last
        else:
            return 0

        step = 1 if self.periodicity == DAILY else 7
        streak = 0
        expected = anchor
        for k in reversed(keys):
            if k == expected:
                streak += 1
                expected -= step
            elif k < expected:
                break
        return streak

    def is_broken(self, now=None):
        """True if the user missed the last full period they should have hit."""
        now = now or datetime.now()
        keys = self._completed_periods()
        today = _period_key(now, self.periodicity)
        step = 1 if self.periodicity == DAILY else 7
        if not keys:
            # freshly created – broken only after a full period has passed
            return _period_key(self.created_at, self.periodicity) + step < today
        last = keys[-1]
        if last == today:
            return False
        return _step(last, self.periodicity) != today

