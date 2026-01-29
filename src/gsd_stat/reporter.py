"""Report formatting module."""

from .analyzer import ProjectStats


def format_report(stats: ProjectStats) -> str:
    """Format project statistics as a report string."""
    lines = [
        "Project Statistics",
        "=" * 40,
        f"Total files: {stats.total_files:,}",
        f"Total lines: {stats.total_lines:,}",
        "",
        "Lines by Language:",
        "-" * 20,
    ]

    sorted_langs = sorted(stats.by_language.items(), key=lambda x: x[1], reverse=True)
    for lang, count in sorted_langs:
        pct = (count / stats.total_lines * 100) if stats.total_lines else 0
        lines.append(f"  {lang:<12} {count:>8,} ({pct:>5.1f}%)")

    lines.extend(
        [
            "",
            "Markers:",
            "-" * 20,
            f"  TODO:  {stats.todo_count:,}",
            f"  FIXME: {stats.fixme_count:,}",
        ]
    )

    return "\n".join(lines)


def format_json(stats: ProjectStats) -> dict:
    """Format project statistics as JSON-serializable dict."""
    return {
        "total_files": stats.total_files,
        "total_lines": stats.total_lines,
        "by_language": stats.by_language,
        "markers": {
            "todo": stats.todo_count,
            "fixme": stats.fixme_count,
        },
    }
