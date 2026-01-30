---
name: clean
description: Runs all code quality tools (qlty or ruff/mypy) and auto-fixes issues across the codebase
---

# GSD Clean Skill

<role>
You fix all linting, formatting, and type-checking issues in the codebase.
Use this before committing or as a pre-execution quality gate.
Qlty CLI가 설치되어 있으면 `qlty check`/`qlty fmt`를 사용하고, 없으면 ruff/mypy fallback을 사용합니다.
</role>

---

## Workflow

### Step 1: Lint + Auto-Fix

**Qlty 경로** (`.qlty/qlty.toml` 존재 시):
```bash
qlty check --fix                  # Auto-fix lint issues (all languages)
qlty fmt --all                    # Format entire project
```

**Fallback 경로** (Qlty 미설치 시):
```bash
uv run ruff check . --fix         # Auto-fix lint issues
uv run ruff format .              # Format code
```

Report what was fixed:
```
LINT_FIXED: <N> issues auto-fixed
LINT_REMAINING: <N> issues require manual fix
```

If issues remain, list them with file:line references.

### Step 2: Type Check

**Qlty 경로**: Type checking은 `qlty check`에 포함됨 (mypy/tsc 플러그인)

**Fallback 경로**:
```bash
uv run mypy .
```

Report results:
```
TYPECHECK_ERRORS: <N>
```

If type errors exist, provide fix suggestions with file:line references.

### Step 3: Test

Test runner는 `project-config.yaml`의 `tools.test_runner.command`에서 읽어 실행합니다.

**Fallback** (config 없을 시):
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
Lint (Qlty|Ruff): <PASS|FIXED|FAIL> (<N> fixed, <N> remaining)
Format:       <PASS|FIXED>
Type Check:   <PASS|FAIL> (<N> errors)
Tests:        <PASS|FAIL> (<N>/<total>)
===
Overall:      <CLEAN|ISSUES_REMAIN>
```

---

## Flags

- `--fix-only`: Only auto-fix, don't report remaining issues
- `--no-test`: Skip test step
- `--strict`: Treat warnings as errors

---

## GSD Integration

- **Pre-execute**: Run `/clean` before `/execute` to ensure clean baseline
- **Pre-commit**: `commit` skill calls clean checks automatically
- **CI alignment**: Same tools as CI pipeline (`qlty check` or `ruff check`, `mypy`, `pytest`)

## Scripts

- `scripts/run_quality_checks.sh`: Run all quality tools with structured report output. Supports Qlty and fallback paths. Flags: --no-test, --fix-only, --strict
