---
description: Capture a todo item for later
argument-hint: "<description> [--priority high|medium|low]"
---

# /add-todo Workflow

<objective>
Quickly capture an idea, task, or issue without interrupting current work flow.
</objective>

<context>
**Item:** $ARGUMENTS (the todo description)

**Flags:**
- `--priority high|medium|low` — Set priority (default: medium)

**Output:**
- `.gsd/TODO.md` — Accumulated todo items
</context>

<process>

## 1. Parse Arguments

Extract:
- Todo description
- Priority (default: medium)

---

## 2. Ensure TODO.md Exists

```bash
if [ ! -f ".gsd/TODO.md" ]; then
    # Create with header
    mkdir -p .gsd
    echo "# TODO" > .gsd/TODO.md
fi
```

---

## 3. Add Todo Item

Append to `.gsd/TODO.md`:

```markdown
- [ ] {description} `{priority}` — {date}
```

---

## 4. Confirm

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► TODO ADDED ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{description}
Priority: {priority}

───────────────────────────────────────────────────────

/check-todos — see all pending items

───────────────────────────────────────────────────────
```

</process>
