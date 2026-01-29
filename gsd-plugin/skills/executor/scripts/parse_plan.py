#!/usr/bin/env python3
"""Parse PLAN.md and extract structured task list.

Extracts tasks from XML-structured PLAN.md files into a machine-readable
format for the executor agent.

Usage:
    python3 scripts/parse_plan.py <plan_file>
    python3 scripts/parse_plan.py .gsd/phases/1/01-PLAN.md
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter as a dict."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    fields = {}
    current_key = None
    current_list: list[str] = []

    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- ") and current_key:
            current_list.append(stripped[2:].strip().strip('"').strip("'"))
        elif ":" in stripped:
            if current_key and current_list:
                fields[current_key] = current_list
                current_list = []

            key, _, value = stripped.partition(":")
            current_key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value and value != "":
                fields[current_key] = value
                current_key = None
        else:
            current_key = None

    if current_key and current_list:
        fields[current_key] = current_list

    return fields


def extract_tag(text: str, tag: str) -> str:
    """Extract content of an XML-like tag."""
    match = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_tasks(content: str) -> list[dict]:
    """Extract all tasks from the plan content."""
    tasks = []
    task_blocks = re.findall(r"<task\b([^>]*)>(.*?)</task>", content, re.DOTALL)

    for attrs, body in task_blocks:
        # Parse task type from attributes
        type_match = re.search(r'type="([^"]*)"', attrs)
        task_type = type_match.group(1) if type_match else "auto"

        task = {
            "type": task_type,
            "name": extract_tag(body, "name"),
            "files": [f.strip() for f in extract_tag(body, "files").split(",") if f.strip()],
            "action": extract_tag(body, "action"),
            "verify": extract_tag(body, "verify"),
            "done": extract_tag(body, "done"),
        }
        tasks.append(task)

    return tasks


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/parse_plan.py <plan_file>", file=sys.stderr)
        sys.exit(1)

    plan_path = Path(sys.argv[1])
    if not plan_path.exists():
        print(json.dumps({"error": f"File not found: {plan_path}"}))
        sys.exit(1)

    content = plan_path.read_text(encoding="utf-8")

    frontmatter = parse_frontmatter(content)
    tasks = parse_tasks(content)

    # Extract objective
    objective = extract_tag(content, "objective")

    # Extract verification checklist
    verification = extract_tag(content, "verification")
    checklist = re.findall(r"- \[[ x]\] (.+)", verification)

    result = {
        "file": str(plan_path),
        "frontmatter": frontmatter,
        "objective": objective,
        "tasks": tasks,
        "task_count": len(tasks),
        "verification_checklist": checklist,
        "autonomous": frontmatter.get("autonomous", "true") == "true",
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Summary to stderr
    phase = frontmatter.get("phase", "?")
    plan = frontmatter.get("plan", "?")
    print(f"\nPlan {phase}.{plan}: {len(tasks)} task(s)", file=sys.stderr)
    for i, t in enumerate(tasks, 1):
        print(f"  {i}. [{t['type']}] {t['name']}", file=sys.stderr)
        if t["files"]:
            print(f"     Files: {', '.join(t['files'])}", file=sys.stderr)


if __name__ == "__main__":
    main()
