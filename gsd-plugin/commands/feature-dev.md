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
Run `analyze_code_impact` on the entities you intend to modify.
```
analyze_code_impact(entityId: "target_module", depth: 2)
```

### 3. Implementation
Write code following the plan. Commit after each sub-task.

### 4. Architecture Check
If the change involves cross-module interaction, run `query` to verify patterns.
```
query("check architecture and module boundaries for src/")
```

### 5. Verification
Run the test suite:
```bash
uv run pytest tests/
```

### 6. Update State
Mark the task as complete in `.gsd/STATE.md`.
Update `.gsd/JOURNAL.md` if a significant milestone was reached.

### 7. Re-index (if new files created)
Use the `index` MCP tool to re-index the codebase.

<related>
## Related

| Command | Relationship |
|---------|--------------|
| `/plan` | Creates PLAN.md files for the phase |
| `/execute` | Runs PLAN.md files with atomic commits |
| `/verify` | Validates executed plans |
| `/debug` | Systematic debugging if issues arise |
</related>
