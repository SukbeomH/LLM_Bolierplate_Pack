#!/usr/bin/env python3
"""Find files that depend on a target module or file.

Scans Python source files for import statements referencing the target,
producing an impact assessment.

Usage:
    python3 scripts/find_dependents.py <target_module_or_file>
    python3 scripts/find_dependents.py src/auth/models.py
    python3 scripts/find_dependents.py auth
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "__pycache__", ".git", "node_modules", ".mypy_cache", ".ruff_cache"}

IMPACT_THRESHOLDS = [(0, 1), (2, 3), (5, 5), (10, 7)]


def _calc_impact_score(dep_count: int) -> int:
    """Calculate impact score (1-9) from dependent count."""
    for threshold, score in IMPACT_THRESHOLDS:
        if dep_count <= threshold:
            return score
    return 9


def _scan_file(py_file: Path, root: Path, patterns: list) -> dict | None:
    """Scan a single file for import matches."""
    try:
        content = py_file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return None

    matches = [
        {"line": line_no, "content": line.strip()}
        for line_no, line in enumerate(content.splitlines(), 1)
        if any(p.search(line) for p in patterns)
    ]
    if not matches:
        return None
    return {"file": str(py_file.relative_to(root)), "references": matches}


def find_dependents(root: Path, target: str) -> dict:
    """Find all files that import or reference the target."""
    target_module = target.replace("/", ".").replace(".py", "").strip(".")
    target_name = target_module.split(".")[-1]

    patterns = [
        re.compile(rf"\bfrom\s+[\w.]*{re.escape(target_name)}[\w.]*\s+import\b"),
        re.compile(rf"\bimport\s+[\w.]*{re.escape(target_name)}\b"),
    ]

    dependents = [
        result
        for py_file in sorted(root.rglob("*.py"))
        if not any(skip in py_file.parts for skip in SKIP_DIRS)
        for result in [_scan_file(py_file, root, patterns)]
        if result is not None
    ]

    impact_score = _calc_impact_score(len(dependents))
    escalation = (
        "AUTO" if impact_score <= 3 else ("WARN" if impact_score <= 6 else "HUMAN_APPROVAL")
    )

    return {
        "target": target,
        "target_module": target_module,
        "dependent_count": len(dependents),
        "impact_score": impact_score,
        "escalation": escalation,
        "dependents": dependents,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/find_dependents.py <target_module_or_file>", file=sys.stderr)
        sys.exit(1)

    target = sys.argv[1]
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    result = find_dependents(root, target)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Human-readable summary to stderr
    print(f"\nImpact Score: {result['impact_score']}/10 ({result['escalation']})", file=sys.stderr)
    print(f"Dependents: {result['dependent_count']} file(s)", file=sys.stderr)
    for dep in result["dependents"]:
        print(f"  {dep['file']} ({len(dep['references'])} ref(s))", file=sys.stderr)

    sys.exit(0 if result["impact_score"] <= 6 else 1)


if __name__ == "__main__":
    main()
