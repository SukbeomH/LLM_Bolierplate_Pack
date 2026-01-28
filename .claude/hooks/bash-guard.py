#!/usr/bin/env python3
"""Hook: PreToolUse (Bash) — 파괴적 명령 + pip/poetry 차단

1. 파괴적 git 명령 차단 (push --force, reset --hard, checkout ., clean -f 등)
2. pip/poetry 사용 차단 (uv 강제)
Exit code 2 = 차단 (stderr가 Claude에게 전달됨)
Exit code 0 = 허용
"""
import json
import re
import sys

# ── 파괴적 git 명령 패턴 ──
DESTRUCTIVE_GIT = [
    (r"git\s+push\s+.*--force", "git push --force is blocked. Use --force-with-lease if absolutely necessary."),
    (r"git\s+push\s+-f\b", "git push -f is blocked. Use --force-with-lease if absolutely necessary."),
    (r"git\s+reset\s+--hard", "git reset --hard is blocked. This discards all local changes."),
    (r"git\s+checkout\s+\.\s*$", "git checkout . is blocked. This discards all uncommitted changes."),
    (r"git\s+clean\s+-f", "git clean -f is blocked. This permanently deletes untracked files."),
    (r"git\s+branch\s+-D\b", "git branch -D is blocked. Use -d (safe delete) instead."),
    (r"git\s+restore\s+\.\s*$", "git restore . is blocked. This discards all working tree changes."),
]

# ── pip/poetry 차단 패턴 ──
WRONG_PKG_MANAGER = [
    (r"\bpip\s+install\b", "Use 'uv add <package>' instead of 'pip install'."),
    (r"\bpip3\s+install\b", "Use 'uv add <package>' instead of 'pip3 install'."),
    (r"\bpoetry\s+add\b", "Use 'uv add <package>' instead of 'poetry add'."),
    (r"\bpoetry\s+install\b", "Use 'uv sync' instead of 'poetry install'."),
    (r"\bconda\s+install\b", "Use 'uv add <package>' instead of 'conda install'."),
]

try:
    data = json.load(sys.stdin)
except (json.JSONDecodeError, EOFError):
    sys.exit(0)

tool_input = data.get("tool_input", {})
command = tool_input.get("command", "")

if not command:
    sys.exit(0)

# 파괴적 git 명령 검사
for pattern, message in DESTRUCTIVE_GIT:
    if re.search(pattern, command):
        print(f"Blocked: {message}", file=sys.stderr)
        sys.exit(2)

# pip/poetry 검사
for pattern, message in WRONG_PKG_MANAGER:
    if re.search(pattern, command):
        print(f"Blocked: {message}", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
