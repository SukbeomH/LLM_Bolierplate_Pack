---
description: Standard workflow for developing a new feature
---

# Feature Development Workflow

<objective>
Guide feature development through the GSD methodology: context check, impact analysis, implementation, verification, and state update.
</objective>

## Prerequisites
- [ ] `.gsd/SPEC.md` is FINALIZED
- [ ] Phase with the feature is defined in `.gsd/ROADMAP.md`
- [ ] Plans exist (run `/plan` first if not)

## Steps

### 1. Context Check
Read the relevant sections of `.gsd/SPEC.md` and `.gsd/ROADMAP.md`.
Load the phase plan from `.gsd/phases/{N}/{M}-PLAN.md`.

### 2. Impact Analysis
Run `agentic_impact` on the files you intend to modify.
```
agentic_impact(file_paths=["src/target_file.py"])
```

### 3. Implementation
Write code following the plan. Commit after each sub-task.

### 4. Architecture Check
If the change involves cross-module interaction, run `agentic_architecture` to verify patterns.

### 5. Verification
Run the test suite:
```bash
uv run pytest tests/
```

### 6. Update State
Mark the task as complete in `.gsd/STATE.md`.
Update `.gsd/JOURNAL.md` if a significant milestone was reached.

### 7. Re-index (if new files created)
```bash
codegraph index . -r --force
```

<related>
## Related

| Command | Relationship |
|---------|--------------|
| `/plan` | Creates PLAN.md files for the phase |
| `/execute` | Runs PLAN.md files with atomic commits |
| `/verify` | Validates executed plans |
| `/debug` | Systematic debugging if issues arise |
</related>
