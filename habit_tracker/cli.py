"""CLI built with Click.

    python -m habit_tracker --help
"""
from datetime import datetime, timedelta
from pathlib import Path

import click

from . import analytics
from .fixtures import predefined_habits
from .habit import DAILY, WEEKLY, Habit
from .storage import DEFAULT_DB, Storage

PERIOD_CHOICE = click.Choice([DAILY, WEEKLY])


def _fmt(h):
    """One-line habit summary used by list/broken/same-period."""
    status = "BROKEN" if h.is_broken() else "OK"
    return (f"  {h.name:<15} [{h.periodicity:<6}] "
            f"done={len(h.completions):<3} "
            f"longest={h.longest_streak():<3} "
            f"current={h.current_streak():<3} {status}")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--db", type=click.Path(dir_okay=False, path_type=Path),
              default=DEFAULT_DB, show_default=True,
              help="Path to the SQLite database file.")
@click.pass_context
def cli(ctx, db):
    """A tiny habit tracker."""
    ctx.obj = {"db": db}


@cli.command()
@click.argument("name")
@click.argument("periodicity", type=PERIOD_CHOICE)
@click.argument("description")
@click.pass_context
def create(ctx, name, periodicity, description):
    """Create a new habit."""
    with Storage(ctx.obj["db"]) as store:
        if store.get(name):
            raise click.ClickException(f"{name!r} already exists.")
        store.add(Habit(name, description, periodicity))
    click.echo(f"Created {name!r} ({periodicity}).")


@cli.command()
@click.argument("name")
@click.pass_context
def delete(ctx, name):
    """Delete a habit and all its check-offs."""
    with Storage(ctx.obj["db"]) as store:
        if not store.delete(name):
            raise click.ClickException(f"No habit named {name!r}.")
    click.echo(f"Deleted {name!r}.")


@cli.command()
@click.argument("name")
@click.option("--at", "at_", type=click.DateTime(), default=None,
              help="Timestamp of the check-off (default: now).")
@click.pass_context
def complete(ctx, name, at_):
    """Check a habit off."""
    with Storage(ctx.obj["db"]) as store:
        try:
            ts = store.check_off(name, at_)
        except KeyError as e:
            raise click.ClickException(str(e))
    click.echo(f"Checked off {name!r} at {ts.isoformat(timespec='seconds')}.")


@cli.command("list")
@click.option("--periodicity", type=PERIOD_CHOICE, default=None,
              help="Filter by periodicity.")
@click.pass_context
def list_(ctx, periodicity):
    """List every habit."""
    with Storage(ctx.obj["db"]) as store:
        habits = store.all()
    if periodicity:
        habits = analytics.by_period(habits, periodicity)
    if not habits:
        click.echo("No habits stored.")
        return
    click.echo(f"{len(habits)} habit(s):")
    for h in habits:
        click.echo(_fmt(h))


@cli.command()
@click.pass_context
def seed(ctx):
    """Load the five predefined habits with 4 weeks of sample data."""
    with Storage(ctx.obj["db"]) as store:
        store.seed(predefined_habits())
    click.echo("Seeded predefined habits.")


@cli.group()
def analyse():
    """Analytics queries."""


@analyse.command("longest")
@click.pass_context
def analyse_longest(ctx):
    """Longest streak across every habit."""
    with Storage(ctx.obj["db"]) as store:
        habits = store.all()
    best = analytics.top_streak_habit(habits)
    if best is None:
        click.echo("No habits stored.")
    else:
        click.echo(f"Longest streak: {best.longest_streak()} ({best.name}).")


@analyse.command("longest-for")
@click.argument("name")
@click.pass_context
def analyse_longest_for(ctx, name):
    """Longest streak for a specific habit."""
    with Storage(ctx.obj["db"]) as store:
        habits = store.all()
    try:
        n = analytics.longest_streak_of(habits, name)
    except KeyError:
        raise click.ClickException(f"No habit named {name!r}.")
    click.echo(f"Longest streak for {name!r}: {n}.")


@analyse.command("same-period")
@click.argument("periodicity", type=PERIOD_CHOICE)
@click.pass_context
def analyse_same_period(ctx, periodicity):
    """List habits sharing a periodicity."""
    with Storage(ctx.obj["db"]) as store:
        habits = store.all()
    hits = analytics.by_period(habits, periodicity)
    if not hits:
        click.echo(f"No {periodicity} habits.")
        return
    for h in hits:
        click.echo(_fmt(h))


@analyse.command("broken")
@click.pass_context
def analyse_broken(ctx):
    """List habits that are currently broken."""
    with Storage(ctx.obj["db"]) as store:
        habits = store.all()
    hits = analytics.broken(habits)
    if not hits:
        click.echo("No broken habits – nice.")
        return
    for h in hits:
        click.echo(_fmt(h))


@analyse.command("struggled")
@click.option("--days", type=int, default=30, show_default=True,
              help="Look-back window in days.")
@click.pass_context
def analyse_struggled(ctx, days):
    """Habits ranked by missed periods in the last N days."""
    with Storage(ctx.obj["db"]) as store:
        habits = store.all()
    since = datetime.now() - timedelta(days=days)
    ranked = analytics.struggled_since(habits, since)
    if not ranked:
        click.echo(f"Nothing missed in the last {days} days.")
        return
    for h, misses in ranked:
        click.echo(f"  {h.name:<15} missed {misses}")


def main():
    cli()
