"""File analysis module."""

from dataclasses import dataclass, field
from pathlib import Path

LANGUAGE_EXTENSIONS: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".sh": "Shell",
    ".toml": "TOML",
}

IGNORE_DIRS: set[str] = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".graph-index",
    ".ruff_cache",
    ".mypy_cache",
    ".pytest_cache",
}


@dataclass
class FileStats:
    """Statistics for a single file."""

    path: Path
    lines: int
    language: str


@dataclass
class ProjectStats:
    """Aggregated project statistics."""

    total_files: int = 0
    total_lines: int = 0
    by_language: dict[str, int] = field(default_factory=dict)
    todo_count: int = 0
    fixme_count: int = 0


def detect_language(path: Path) -> str:
    """Detect programming language from file extension."""
    return LANGUAGE_EXTENSIONS.get(path.suffix.lower(), "Other")


def count_lines(path: Path) -> int:
    """Count lines in a file."""
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
        return 0


def count_markers(path: Path) -> tuple[int, int]:
    """Count TODO and FIXME markers in a file."""
    try:
        content = path.read_text(encoding="utf-8").upper()
        return content.count("TODO"), content.count("FIXME")
    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
        return 0, 0


def should_ignore(path: Path) -> bool:
    """Check if path should be ignored."""
    return any(part in IGNORE_DIRS for part in path.parts)


def analyze_file(path: Path) -> FileStats:
    """Analyze a single file."""
    return FileStats(
        path=path,
        lines=count_lines(path),
        language=detect_language(path),
    )


def analyze_project(root: Path) -> ProjectStats:
    """Analyze entire project directory."""
    stats = ProjectStats()

    for path in root.rglob("*"):
        if not path.is_file() or should_ignore(path):
            continue

        file_stats = analyze_file(path)
        stats.total_files += 1
        stats.total_lines += file_stats.lines

        lang = file_stats.language
        stats.by_language[lang] = stats.by_language.get(lang, 0) + file_stats.lines

        todos, fixmes = count_markers(path)
        stats.todo_count += todos
        stats.fixme_count += fixmes

    return stats
