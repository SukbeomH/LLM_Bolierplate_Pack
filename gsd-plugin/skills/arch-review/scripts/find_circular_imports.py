#!/usr/bin/env python3
"""Detect circular import dependencies in Python source files.

Builds an import graph and finds cycles using DFS.

Usage:
    python3 scripts/find_circular_imports.py [path]
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

IMPORT_RE = re.compile(r"^\s*(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))", re.MULTILINE)


def build_import_graph(root: Path) -> dict[str, set[str]]:
    """Build directed graph: module -> set of imported modules."""
    skip_dirs = {".venv", "__pycache__", ".git", "node_modules", ".mypy_cache"}
    graph: dict[str, set[str]] = defaultdict(set)
    module_files: dict[str, str] = {}

    for py_file in sorted(root.rglob("*.py")):
        if any(skip in py_file.parts for skip in skip_dirs):
            continue

        rel = py_file.relative_to(root)
        # Convert path to module name
        parts = list(rel.parts)
        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = parts[-1].replace(".py", "")
        module_name = ".".join(parts)

        if not module_name:
            continue

        module_files[module_name] = str(rel)

        try:
            content = py_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        for match in IMPORT_RE.finditer(content):
            imported = match.group(1) or match.group(2)
            if imported:
                graph[module_name].add(imported)

    return graph


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Find all cycles in the import graph using DFS."""
    cycles: list[list[str]] = []
    visited: set[str] = set()
    rec_stack: set[str] = set()
    path: list[str] = []

    def dfs(node: str) -> None:
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited and neighbor in graph:
                dfs(neighbor)
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                # Normalize cycle (start from smallest)
                min_idx = cycle.index(min(cycle[:-1]))
                normalized = cycle[min_idx:-1] + cycle[:min_idx] + [cycle[min_idx]]
                if normalized not in cycles:
                    cycles.append(normalized)

        path.pop()
        rec_stack.discard(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return cycles


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    graph = build_import_graph(root)
    cycles = find_cycles(graph)

    result = {
        "modules_scanned": len(graph),
        "cycles_found": len(cycles),
        "status": "CIRCULAR_DEPS" if cycles else "CLEAN",
        "cycles": [{"chain": c, "length": len(c) - 1} for c in cycles],
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if cycles:
        print(f"\nCIRCULAR_DEPS: {len(cycles)} cycle(s) found", file=sys.stderr)
        for i, c in enumerate(cycles, 1):
            print(f"  {i}. {' -> '.join(c)}", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nCLEAN: No circular imports detected", file=sys.stderr)


if __name__ == "__main__":
    main()
