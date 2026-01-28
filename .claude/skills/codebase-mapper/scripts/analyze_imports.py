#!/usr/bin/env python3
"""Analyze Python import dependency graph.

Scans Python source files, extracts import statements, and builds a
dependency map showing which modules depend on which.

Usage:
    python3 scripts/analyze_imports.py [path] [--json]
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE)


def extract_imports(filepath: Path) -> list[str]:
    """Extract import module names from a Python file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return []

    imports = []
    for match in IMPORT_RE.finditer(content):
        module = match.group(1) or match.group(2)
        if module:
            imports.append(module.split(".")[0])
    return list(set(imports))


def scan_project(root: Path) -> dict:
    """Build import dependency graph for the project."""
    skip_dirs = {".venv", "__pycache__", ".git", "node_modules", ".mypy_cache", ".ruff_cache"}

    # Find all Python modules in the project
    project_modules: set[str] = set()
    file_imports: dict[str, list[str]] = {}

    for py_file in sorted(root.rglob("*.py")):
        if any(skip in py_file.parts for skip in skip_dirs):
            continue

        rel_path = str(py_file.relative_to(root))
        imports = extract_imports(py_file)
        file_imports[rel_path] = imports

        # Infer module name
        parts = py_file.relative_to(root).parts
        if parts:
            project_modules.add(parts[0].replace(".py", ""))

    # Separate internal vs external imports
    internal_deps: dict[str, list[str]] = defaultdict(list)
    external_deps: dict[str, int] = defaultdict(int)

    for filepath, imports in file_imports.items():
        for imp in imports:
            if imp in project_modules:
                internal_deps[filepath].append(imp)
            else:
                external_deps[imp] += 1

    return {
        "total_files": len(file_imports),
        "project_modules": sorted(project_modules),
        "internal_dependencies": dict(internal_deps),
        "external_packages": dict(sorted(external_deps.items(), key=lambda x: -x[1])),
        "most_imported_external": sorted(external_deps.items(), key=lambda x: -x[1])[:10],
    }


def main() -> None:
    target = (
        Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else Path(".")
    )
    output_json = "--json" in sys.argv

    result = scan_project(target)

    if output_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("=== Import Analysis ===")
        print(f"Files scanned: {result['total_files']}")
        print(f"Project modules: {', '.join(result['project_modules']) or 'none'}")
        print()

        if result["internal_dependencies"]:
            print("## Internal Dependencies")
            for filepath, deps in sorted(result["internal_dependencies"].items()):
                print(f"  {filepath} -> {', '.join(deps)}")
            print()

        if result["most_imported_external"]:
            print("## Top External Packages")
            for pkg, count in result["most_imported_external"]:
                print(f"  {pkg}: {count} file(s)")


if __name__ == "__main__":
    main()
