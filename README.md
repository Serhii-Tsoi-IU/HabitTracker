# Habit Tracker

A small Python backend for tracking daily and weekly habits.
Built as a course project – kept intentionally small and hopefully readable.

Features:

- Daily and weekly habits with streak tracking
- SQLite persistence (no server, just a file)
- A `click`-based command line
- Five predefined habits with 4 weeks of sample data
- A small pytest suite

## Requirements

Python 3.10 or later (I use `X | None` unions in a couple of places).
The only third-party dependency is `click`; `pytest` is used for the tests.

## Install

```bash
cd HabitTracker
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Quick start

```bash
# load 5 predefined habits with 4 weeks of sample data
python -m habit_tracker seed

# see what's in the DB
python -m habit_tracker list

# create your own habit
python -m habit_tracker create meditate daily "10 min meditation"

# check it off (now, or at a specific time)
python -m habit_tracker complete meditate
python -m habit_tracker complete meditate --at 2026-07-30T08:00:00

# delete it
python -m habit_tracker delete meditate
```

`python main.py …` does the same thing – it's just a convenience launcher
that some IDEs like better.

The database defaults to `~/.habit_tracker.db`. Override it with the top
level `--db` option:

```bash
python -m habit_tracker --db ./my.db seed
python -m habit_tracker --db ./my.db list
```

## Analytics

```bash
python -m habit_tracker analyse longest              # best streak, all habits
python -m habit_tracker analyse longest-for brush_teeth
python -m habit_tracker analyse same-period daily
python -m habit_tracker analyse broken
python -m habit_tracker analyse struggled --days 30
```

Everything under `analyse` is a thin wrapper around the pure functions in
`habit_tracker/analytics.py`.

## Running the tests

```bash
python -m pytest
```

