"""CLI entry point."""

import json
import sys
from pathlib import Path

from .analyzer import analyze_project
from .reporter import format_json, format_report


def main(args: list[str] | None = None) -> int:
    """Main CLI entry point."""
    if args is None:
        args = sys.argv[1:]

    # Parse arguments
    show_json = "--json" in args
    paths = [a for a in args if not a.startswith("-")]
    target = Path(paths[0]) if paths else Path.cwd()

    if not target.exists():
        print(f"Error: Path does not exist: {target}", file=sys.stderr)
        return 1

    # Analyze and report
    stats = analyze_project(target)

    if show_json:
        print(json.dumps(format_json(stats), indent=2))
    else:
        print(format_report(stats))

    return 0


if __name__ == "__main__":
    sys.exit(main())
