---
name: context-health-monitor
description: Monitors context complexity and triggers state dumps before quality degrades
---

# Context Health Monitor

## Purpose

Prevent "Context Rot" — the quality degradation that occurs as the agent processes more information in a single session.

## When This Skill Activates

The agent should self-monitor for these warning signs:

### Warning Signs

| Signal | Threshold | Action |
|--------|-----------|--------|
| Repeated debugging | 3+ failed attempts | Trigger state dump |
| Going in circles | Same approach tried twice | Stop and reassess |
| Confusion indicators | "I'm not sure", backtracking | Document uncertainty |
| Context window filling | >60% token usage | Run `/compact` proactively |
| Session length | Extended back-and-forth | Recommend `/pause` or `/handoff` |

## Behavior Rules

### Rule 1: The 3-Strike Rule

If debugging the same issue fails 3 times:

1. **STOP** attempting fixes
2. **Document** in `.gsd/STATE.md`:
   - What was tried
   - What errors occurred
   - Current hypothesis
3. **Recommend** user start fresh session
4. **Do NOT** continue with more attempts

### Rule 2: Circular Detection

If the same approach is being tried again:

1. **Acknowledge** the repetition
2. **List** what has already been tried
3. **Propose** a fundamentally different approach
4. **Or** recommend `/pause` for fresh perspective

### Rule 3: Uncertainty Logging

When uncertain about an approach:

1. **State** the uncertainty clearly
2. **Document** in `.gsd/DECISIONS.md`:
   - The uncertain decision
   - Why it's uncertain
   - Alternatives considered
3. **Ask** user for guidance rather than guessing

### Rule 4: Proactive Compaction

When context window usage exceeds ~60%:

1. **Run** `/compact` before auto-compaction kicks in (~80%)
2. **If task is nearly done**: finish first, then compact
3. **If task is complex with much remaining work**: compact now to preserve budget
4. **If context is beyond recovery** (repeated compactions, degrading quality): use `/handoff` and start fresh

## State Dump Format

When triggered, write to `.gsd/STATE.md`:

```markdown
## Context Health: State Dump

**Triggered**: [date/time]
**Reason**: [3 failures / circular / uncertainty]

### What Was Attempted
1. [Approach 1] — Result: [outcome]
2. [Approach 2] — Result: [outcome]
3. [Approach 3] — Result: [outcome]

### Current Hypothesis
[Best guess at root cause]

### Recommended Next Steps
1. [Fresh perspective action]
2. [Alternative approach to try]

### Files Involved
- [file1.ext] — [what state it's in]
- [file2.ext] — [what state it's in]
```

## Integration

This skill integrates with:
- `/compact` — Proactive context compaction (Rule 4)
- `/handoff` — Lightweight session transfer when context is beyond recovery
- `/pause` — Full GSD session handoff with state archival
- `/resume` — Loads the state dump context
- `.gemini/GEMINI.md` Rule 3 (Context Hygiene) — After 3 failed debug attempts: STOP, summarize to STATE.md, document blocker in DECISIONS.md, recommend fresh session

## Scripts

- `scripts/dump_state.sh`: Dump current context state to .gsd/STATE.md with git info, task status, and recommendations
