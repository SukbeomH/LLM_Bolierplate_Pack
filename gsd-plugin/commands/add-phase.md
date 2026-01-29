---
description: Add a new phase to the end of the roadmap
argument-hint: "<phase-name>"
---

# /add-phase Workflow

<objective>
Add a new phase to the end of the current roadmap.
</objective>

<process>

## 1. Validate Roadmap Exists

```bash
if [ ! -f ".gsd/ROADMAP.md" ]; then
    echo "Error: ROADMAP.md required. Run /new-milestone first." >&2
    exit 1
fi
```

---

## 2. Determine Next Phase Number

```bash
# Count existing phases
phase_count=$(grep -c "### Phase [0-9]" ".gsd/ROADMAP.md")
next_phase=$((phase_count + 1))
```

---

## 3. Gather Phase Information

Ask for:
- **Name** — Phase title
- **Objective** — What this phase achieves
- **Depends on** — Previous phases (usually N-1)

---

## 4. Add to ROADMAP.md

Append:
```markdown
---

### Phase {N}: {name}
**Status**: ⬜ Not Started
**Objective**: {objective}
**Depends on**: Phase {N-1}

**Tasks**:
- [ ] TBD (run /plan {N} to create)

**Verification**:
- TBD
```

---

## 5. Update STATE.md

Note phase added.

---

## 6. Commit

```bash
git add .gsd/ROADMAP.md .gsd/STATE.md
git commit -m "docs: add phase {N} - {name}"
```

---

## 7. Offer Next Steps

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► PHASE ADDED ✓
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase {N}: {name}

───────────────────────────────────────────────────────

▶ NEXT

/plan {N} — Create execution plans for this phase

───────────────────────────────────────────────────────
```

</process>
