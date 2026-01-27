---
description: Standard workflow for fixing a bug
---

# Bug Fix Workflow

<objective>
Guide bug fix through the GSD methodology: reproduce, locate, analyze impact, fix, verify, and update state.
</objective>

## Prerequisites
- [ ] Bug is reproducible
- [ ] Issue is documented in `.gsd/TODO.md` or `.gsd/ROADMAP.md`

## Steps

### 1. Reproduce
Confirm the bug exists. Document reproduction steps.

### 2. Locate
Use `agentic_context` to find relevant code.
```
agentic_context(query="ErrorComponent")
```

### 3. Impact Analysis
Identify all affected paths before fixing.
```
agentic_impact(file_paths=["src/buggy_file.py"])
```

### 4. Fix
Implement the minimal change that resolves the issue.

### 5. Test
Run the test suite to confirm the fix doesn't break anything.
```bash
uv run pytest tests/
```

### 6. Regression Check
If dependencies were affected, add tests for them.

### 7. Update State
Mark the bug as resolved in `.gsd/STATE.md`.
Log the fix in `.gsd/JOURNAL.md`.

<related>
## Related

| Command | Relationship |
|---------|--------------|
| `/debug` | Systematic debugging for complex bugs |
| `/verify` | Validates the fix against requirements |
| `/execute` | For planned bug-fix tasks |
</related>
