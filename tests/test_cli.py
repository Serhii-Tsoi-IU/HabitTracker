"""End-to-end CLI smoke tests via click's CliRunner."""
from click.testing import CliRunner

from habit_tracker.cli import cli


def _run(db, *args):
    return CliRunner().invoke(cli, ["--db", str(db), *args])


def test_seed_then_list_shows_predefined_habits(tmp_path):
    db = tmp_path / "cli.db"
    assert _run(db, "seed").exit_code == 0
    out = _run(db, "list").output
    for name in ("brush_teeth", "drink_water", "read_book",
                 "exercise", "clean_room"):
        assert name in out


def test_create_complete_delete_full_lifecycle(tmp_path):
    db = tmp_path / "cli.db"
    assert _run(db, "create", "yoga", "daily", "morning yoga").exit_code == 0
    assert _run(db, "complete", "yoga").exit_code == 0
    assert "yoga" in _run(db, "list").output
    assert _run(db, "delete", "yoga").exit_code == 0
    assert "yoga" not in _run(db, "list").output


def test_analyse_longest_reports_best_streak(tmp_path):
    db = tmp_path / "cli.db"
    _run(db, "seed")
    result = _run(db, "analyse", "longest")
    assert result.exit_code == 0
    assert "28" in result.output          # brush_teeth's streak

