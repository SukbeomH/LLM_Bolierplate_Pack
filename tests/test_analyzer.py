"""Tests for analyzer module."""

from pathlib import Path

from gsd_stat.analyzer import (
    analyze_file,
    analyze_project,
    count_lines,
    count_markers,
    detect_language,
    should_ignore,
)


class TestDetectLanguage:
    """Tests for detect_language function."""

    def test_python_file(self) -> None:
        assert detect_language(Path("test.py")) == "Python"

    def test_javascript_file(self) -> None:
        assert detect_language(Path("app.js")) == "JavaScript"

    def test_unknown_extension(self) -> None:
        assert detect_language(Path("file.xyz")) == "Other"

    def test_case_insensitive(self) -> None:
        assert detect_language(Path("TEST.PY")) == "Python"


class TestCountLines:
    """Tests for count_lines function."""

    def test_counts_lines(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3")
        assert count_lines(test_file) == 3

    def test_empty_file(self, tmp_path: Path) -> None:
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        assert count_lines(test_file) == 0

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        assert count_lines(tmp_path / "missing.txt") == 0


class TestCountMarkers:
    """Tests for count_markers function."""

    def test_counts_todo(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("# TODO: fix this\n# TODO: another")
        todos, fixmes = count_markers(test_file)
        assert todos == 2
        assert fixmes == 0

    def test_counts_fixme(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("# FIXME: urgent")
        todos, fixmes = count_markers(test_file)
        assert todos == 0
        assert fixmes == 1

    def test_case_insensitive(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("# todo: lowercase")
        todos, _ = count_markers(test_file)
        assert todos == 1


class TestShouldIgnore:
    """Tests for should_ignore function."""

    def test_ignores_git(self) -> None:
        assert should_ignore(Path(".git/config"))

    def test_ignores_venv(self) -> None:
        assert should_ignore(Path(".venv/lib/python"))

    def test_allows_normal_path(self) -> None:
        assert not should_ignore(Path("src/main.py"))


class TestAnalyzeFile:
    """Tests for analyze_file function."""

    def test_returns_file_stats(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')\n")
        stats = analyze_file(test_file)
        assert stats.path == test_file
        assert stats.lines == 1
        assert stats.language == "Python"


class TestAnalyzeProject:
    """Tests for analyze_project function."""

    def test_analyzes_directory(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("line1\nline2")
        (tmp_path / "b.py").write_text("line1")
        stats = analyze_project(tmp_path)
        assert stats.total_files == 2
        assert stats.total_lines == 3
        assert stats.by_language["Python"] == 3

    def test_ignores_venv(self, tmp_path: Path) -> None:
        venv = tmp_path / ".venv"
        venv.mkdir()
        (venv / "lib.py").write_text("ignored")
        (tmp_path / "main.py").write_text("included")
        stats = analyze_project(tmp_path)
        assert stats.total_files == 1
