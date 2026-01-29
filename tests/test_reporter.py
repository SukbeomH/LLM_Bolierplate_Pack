"""Tests for reporter module."""

from gsd_stat.analyzer import ProjectStats
from gsd_stat.reporter import format_json, format_report


class TestFormatReport:
    """Tests for format_report function."""

    def test_includes_totals(self) -> None:
        stats = ProjectStats(total_files=10, total_lines=500)
        report = format_report(stats)
        assert "Total files: 10" in report
        assert "Total lines: 500" in report

    def test_includes_language_breakdown(self) -> None:
        stats = ProjectStats(
            total_files=2,
            total_lines=100,
            by_language={"Python": 80, "JavaScript": 20},
        )
        report = format_report(stats)
        assert "Python" in report
        assert "JavaScript" in report

    def test_includes_markers(self) -> None:
        stats = ProjectStats(todo_count=5, fixme_count=2)
        report = format_report(stats)
        assert "TODO:  5" in report
        assert "FIXME: 2" in report


class TestFormatJson:
    """Tests for format_json function."""

    def test_returns_dict(self) -> None:
        stats = ProjectStats(total_files=5, total_lines=100)
        result = format_json(stats)
        assert isinstance(result, dict)
        assert result["total_files"] == 5
        assert result["total_lines"] == 100

    def test_includes_markers(self) -> None:
        stats = ProjectStats(todo_count=3, fixme_count=1)
        result = format_json(stats)
        assert result["markers"]["todo"] == 3
        assert result["markers"]["fixme"] == 1
