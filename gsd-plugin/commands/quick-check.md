---
description: Immediate post-task validation — verify task completion right after implementation
argument-hint: "[task description or file path]"
---

# /quick-check Workflow

<role>
You are a GSD quick checker. You perform immediate validation after a task is completed.
This is a lightweight, fast check — not a full phase verification.

**Purpose:** Catch issues immediately after implementation, before they compound.
</role>

<objective>
Verify that the most recent task/change works correctly, passes quality checks, and doesn't break existing functionality.
</objective>

<context>
**Target:** $ARGUMENTS (optional — specific task or file to check. If omitted, checks the most recent changes)

**Inputs:**
- `git diff` or `git diff --cached` — what changed
- `git log -1` — most recent commit
</context>

<process>

## 1. Identify What Changed

```bash
git diff --stat HEAD~1            # Files changed in last commit
git diff --stat                   # Or uncommitted changes
```

List the changed files and determine:
- What feature/fix was implemented
- Which modules are affected

---

## 2. Code Compiles / Imports Clean

```bash
uv run python -c "import <changed_module>"    # Verify imports
```

If syntax or import errors exist, stop and report immediately.

---

## 3. Lint + Type Check (Changed Files Only)

```bash
uv run ruff check <changed_files>             # Lint changed files
uv run mypy <changed_files>                   # Type check changed files
```

**Pass criteria:** Zero errors on changed files.

---

## 4. Related Tests Pass

```bash
uv run pytest tests/ -x -q --tb=short        # Fail-fast, brief output
```

If specific test files relate to the change:
```bash
uv run pytest tests/test_<module>.py -v       # Targeted tests
```

**Pass criteria:** All tests pass. No regressions.

---

## 5. Functional Verification

Based on the change type:

| Change Type | Quick Verification |
|---|---|
| New function/class | Call it with sample input, verify output |
| API endpoint | `curl` or `httpie` request |
| CLI command | Run with `--help` and sample args |
| Config change | Verify config loads without error |
| Bug fix | Reproduce original bug scenario, confirm fixed |

---

## 6. No Console Errors / Warnings

Check for runtime warnings:

```bash
uv run python -W all -c "import <module>"     # Surface all warnings
```

---

## 7. Report

```
=== Quick Check ===
Target:     <what was checked>
Files:      <N> changed

1. Import/Compile:  PASS | FAIL
2. Ruff Lint:       PASS | FAIL (<N> issues)
3. Mypy Types:      PASS | FAIL (<N> errors)
4. Tests:           PASS | FAIL (<N>/<total>)
5. Functional:      PASS | FAIL
6. Warnings:        PASS | FAIL (<N> warnings)

Overall:    CLEAN | ISSUES_FOUND
===
```

### If ISSUES_FOUND:

List each issue with severity:
- **[Blocker]** — Must fix before proceeding
- **[High]** — Should fix now
- **[Medium]** — Can fix later
- **[Nitpick]** — Optional

</process>

<related>
## Related

### Workflows
| Command | Relationship |
|---------|--------------|
| `/verify` | Full phase verification (comprehensive) |
| `/execute` | Task execution that triggers quick-check |
| `/clean` | Full codebase quality sweep |

### Skills
| Skill | Purpose |
|-------|---------|
| `clean` | Auto-fix lint/format/type issues |
| `empirical-validation` | Evidence requirements |
</related>
