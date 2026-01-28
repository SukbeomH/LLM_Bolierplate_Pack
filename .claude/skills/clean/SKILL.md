---
name: clean
description: Runs all code quality tools (ruff, mypy) and auto-fixes issues across the codebase
---

# GSD Clean Skill

<role>
You fix all linting, formatting, and type-checking issues in the codebase.
Use this before committing or as a pre-execution quality gate.
</role>

---

## Workflow

### Step 1: Ruff — Lint + Auto-Fix

```bash
uv run ruff check . --fix         # Auto-fix lint issues
uv run ruff format .              # Format code
```

Report what was fixed:
```
RUFF_FIXED: <N> issues auto-fixed
RUFF_REMAINING: <N> issues require manual fix
```

If issues remain, list them with file:line references.

### Step 2: Mypy — Type Check

```bash
uv run mypy .
```

Report results:
```
MYPY_ERRORS: <N>
MYPY_WARNINGS: <N>
```

If type errors exist, provide fix suggestions with file:line references.

### Step 3: Pytest — Quick Smoke Test

```bash
uv run pytest tests/ -x -q --tb=short
```

Report results:
```
TESTS_PASSED: <N>/<total>
TESTS_FAILED: <N> (if any)
```

---

## Output Summary

```
=== Clean Report ===
Ruff Lint:    <PASS|FIXED|FAIL> (<N> fixed, <N> remaining)
Ruff Format:  <PASS|FIXED>
Mypy:         <PASS|FAIL> (<N> errors)
Tests:        <PASS|FAIL> (<N>/<total>)
===
Overall:      <CLEAN|ISSUES_REMAIN>
```

---

## Flags

- `--fix-only`: Only auto-fix, don't report remaining issues
- `--no-test`: Skip pytest step
- `--strict`: Treat warnings as errors

---

## GSD Integration

- **Pre-execute**: Run `/clean` before `/execute` to ensure clean baseline
- **Pre-commit**: `commit` skill calls clean checks automatically
- **CI alignment**: Same tools as CI pipeline (`ruff check`, `mypy`, `pytest`)

## Scripts

- `scripts/run_quality_checks.sh`: Run all quality tools (ruff lint, format, mypy, pytest) with structured report output. Flags: --no-test, --fix-only, --strict
