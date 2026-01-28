---
description: Lightweight session handoff — create HANDOFF.md for clean context transfer
---

# /handoff Workflow

<objective>
Create a concise HANDOFF.md for transferring context to a fresh session.
Lighter than `/pause` — no GSD state management, just the essentials for continuity.
</objective>

<when_to_use>
- Quick session transfer without full GSD state dump
- Handing off to a different agent or team member
- Before starting a fresh conversation on the same task
- When `/pause` feels too heavy for the situation
</when_to_use>

<process>

## 1. Create or Update HANDOFF.md

Write to `HANDOFF.md` in the project root:

```markdown
# [Task Name] — Handoff

**Date**: YYYY-MM-DD HH:MM
**Branch**: {current git branch}

## Goal
{What we're trying to accomplish — 1-2 sentences}

## Current Progress
- {Completed item 1}
- {Completed item 2}
- {In-progress item, if any}

## What Worked
- {Successful approach and why}

## What Didn't Work
- {Failed approach 1} — {why it failed}
- {Failed approach 2} — {why it failed}

## Next Steps
1. {Most important action}
2. {Second priority}
3. {Third priority}

## Key Files
- `{file1}` — {what's relevant}
- `{file2}` — {what's relevant}
```

---

## 2. Verify Completeness

Before saving, check:
- [ ] Goal is specific enough for a stranger to understand
- [ ] "What Didn't Work" includes at least one entry (even if "nothing failed")
- [ ] Next Steps are actionable (not vague)
- [ ] Key Files listed so new session can navigate immediately

---

## 3. Display Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 HANDOFF READY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Saved to: HANDOFF.md

To resume in a new session:

  "Read HANDOFF.md and continue from where we left off."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

</process>

<design_rationale>
This workflow is intentionally minimal compared to `/pause`:

| Aspect | /handoff | /pause |
|--------|----------|--------|
| Output | HANDOFF.md (root) | STATE.md + JOURNAL.md (.gsd/) |
| Weight | ~20 lines | ~60 lines |
| GSD required | No | Yes |
| "What Didn't Work" | Explicit section | Implicit in "Approaches Tried" |
| Use case | Quick transfer | Full session archival |

The "What Didn't Work" section is critical — it prevents a fresh agent from repeating failed approaches. This is the single most valuable piece of context for session continuity.
</design_rationale>
