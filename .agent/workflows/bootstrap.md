---
description: Complete initial project setup — deps, MCP, indexing, analysis, memory
---

# /bootstrap Workflow

<role>
You are a GSD bootstrap orchestrator. You set up a freshly cloned boilerplate project from zero to fully operational in one pass.

**Core responsibilities:**
- Verify system prerequisites
- Set up Python environment
- Connect MCP servers
- Index the codebase
- Analyze and document architecture
- Store initial memory state
- Report final status
</role>

<objective>
Perform complete first-time project setup: system dependency verification, Python environment, MCP server connection, code indexing, codebase analysis, and memory initialization.

This is the first command to run after cloning the boilerplate into a new project. It validates everything needed for the GSD workflow and AI-assisted development.

**Creates/Verifies:**
- `.venv/` — Python virtual environment
- `.env` — Environment configuration
- `.patch-workspace/` — Patched Claude Code CLI (optional, ~50% token reduction)
- `.code-graph-rag/` — Code index data
- `.gsd/ARCHITECTURE.md` — System architecture documentation
- `.gsd/STACK.md` — Technology stack documentation
- Bootstrap memory record in memorygraph

**After this command:** Run `/new-project` or `/plan 1` to begin development.
</objective>

<context>
**No arguments required.** Operates on current project directory.

**Prerequisites:**
- Boilerplate cloned or initialized
- `.mcp.json` exists in project root
- `pyproject.toml` exists in project root

**Related make target:** `make setup` (simpler alternative without MCP/memory integration)
</context>

<process>

## Step 0: Idempotency Check

Before running any setup, check if bootstrap has already been completed:

```
search_memories(tags: ["bootstrap", "init"])
```

Also check for existing artifacts:

```bash
HAS_VENV=$(test -d .venv && echo "yes" || echo "no")
HAS_ENV=$(test -f .env && echo "yes" || echo "no")
HAS_INDEX=$(test -d .code-graph-rag && echo "yes" || echo "no")
HAS_ARCH=$(test -f .gsd/ARCHITECTURE.md && echo "yes" || echo "no")
HAS_PATCH=$(test -d .patch-workspace && echo "yes" || echo "no")
```

**If bootstrap memory exists AND all artifacts present:**

```
================================================================
 BOOTSTRAP: Already completed
================================================================

Previous bootstrap found. All artifacts exist.

Options:
  A) Re-bootstrap — Run full setup again (overwrites existing)
  B) Status check — Show current environment status only
  C) Cancel — Exit without changes

Select [A/B/C]:
================================================================
```

Wait for user selection:
- **A) Re-bootstrap:** Continue to Step 1.
- **B) Status check:** Jump to Step 9 (status report only).
- **C) Cancel:** Exit.

**If no bootstrap memory OR missing artifacts:** Continue to Step 1.

---

## Step 1: System Prerequisites

Display banner:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD >>> BOOTSTRAP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Run system prerequisite checks:

```bash
bash scripts/bootstrap.sh
```

**If exit 1 (required check failed):**
```
BOOTSTRAP STOPPED: Missing required system dependencies.
Install the tools listed above, then re-run /bootstrap.
```
Exit workflow.

**If exit 0:** Record tool versions. Continue.

---

## Step 2: Python Dependencies

```bash
uv sync
```

Verify:
```bash
test -d .venv && echo "PASS: .venv ready" || echo "FAIL: .venv not created"
```

**If fails:** STOP. Display:
```
BOOTSTRAP STOPPED: uv sync failed.
Check pyproject.toml and Python version (>= 3.11 required).
```

**If passes:** Continue.

---

## Step 3: Environment Setup

```bash
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
else
    echo ".env already exists — skipping"
fi
```

---

## Step 4: Prompt Patching (Optional)

Reduce Claude Code system prompt token usage by ~50%. See `.gsd/GUIDE-system-prompt-patch.md`.

**Check prerequisites:**

```bash
CLAUDE_VER=$(claude --version 2>/dev/null | awk '{print $1}')
test -d "claude-code-tips/system-prompt/${CLAUDE_VER}"
```

**If `claude` CLI not found OR patch directory missing:** Record SKIP. Continue to Step 5.

**If `.patch-workspace/` already exists:** Record PASS (already patched). Continue.

**If prerequisites available and `.patch-workspace/` does not exist:**

```bash
make patch-prompt
```

Verify:
```bash
test -d .patch-workspace && echo "PASS" || echo "WARN"
```

**If `make patch-prompt` fails:** Record WARN. Continue. Patching can be retried later with `make patch-prompt`.

---

## Step 5: MCP Server Verification

Test each MCP server connection:

### 4a. graph-code
```
get_graph_health()
```
Record: PASS or FAIL.

### 4b. memorygraph
```
get_memory_statistics()
```
Record: PASS or FAIL.

### 4c. context7 (optional)
```
resolve-library-id(libraryName: "langchain")
```
Record: PASS or WARN (failure is acceptable).

**If graph-code FAIL:** Skip Step 6 (indexing).
**If memorygraph FAIL:** Skip Step 8 (memory store).

---

## Step 6: Code Index

**Skip if:** graph-code failed in Step 4.

```
index(".")
```

Verify results:
```
get_graph_stats()
```

Record entity count and file count.

**If fails:** Record FAIL. Continue. Suggest `make index` or `/map` for retry.

---

## Step 7: Codebase Analysis

Delegate to the `codebase-mapper` skill:
- Generate `.gsd/ARCHITECTURE.md`
- Generate `.gsd/STACK.md`

**If fails:** Record FAIL. Continue.

---

## Step 8: Initial Memory

**Skip if:** memorygraph failed in Step 5.

```
store_memory(
  type: "bootstrap",
  title: "Project Bootstrap",
  content: "Bootstrap completed. System prerequisites verified. MCP servers connected. Codebase indexed. Documentation generated.",
  tags: ["bootstrap", "init", "setup"]
)
```

**If fails:** Record WARN. Continue.

---

## Step 9: Status Report

Output structured report:

```
================================================================
 BOOTSTRAP STATUS REPORT
================================================================
System Prerequisites:  {PASS|FAIL} ({tool versions})
Python Environment:    {PASS|FAIL} (uv synced, .venv ready)
Environment:           {PASS|FAIL} (.env configured)
Prompt Patch:          {PASS|WARN|SKIP} (.patch-workspace ready)
MCP Servers:           graph-code {PASS|FAIL} / memorygraph {PASS|FAIL} / context7 {PASS|WARN}
Code Index:            {PASS|FAIL|SKIP} ({N} entities, {M} files)
Documentation:         {PASS|FAIL} (ARCHITECTURE.md, STACK.md)
Memory:                {PASS|WARN|SKIP} (bootstrap record stored)
================================================================
 RESULT: READY / NEEDS ATTENTION
================================================================
```

**READY:** All critical steps passed (WARN/SKIP acceptable).
**NEEDS ATTENTION:** Any required step FAIL.

</process>

<offer_next>

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD >>> BOOTSTRAP COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

───────────────────────────────────────────────────────

 NEXT

/new-project — Initialize a new GSD project
/plan 1      — Create Phase 1 execution plans
/map         — Re-analyze codebase architecture

───────────────────────────────────────────────────────
```

</offer_next>

<related>
## Related

### Workflows
| Command | Relationship |
|---------|--------------|
| `/new-project` | Run after bootstrap to initialize GSD project |
| `/map` | Re-run codebase analysis if bootstrap mapping failed |
| `/plan` | Start planning after project is bootstrapped |

### Skills
| Skill | Purpose |
|-------|---------|
| `codebase-mapper` | Delegated to in Step 7 for architecture analysis |
| `arch-review` | Uses indexed codebase from bootstrap for validation |
| `executor` | Uses MCP connections verified by bootstrap |

### Make Targets
| Target | Relationship |
|--------|--------------|
| `make setup` | Simpler alternative (no MCP verification, no memory) |
| `make check-deps` | Subset of Step 1 (system prerequisites only) |
| `make patch-prompt` | Subset of Step 4 (prompt patching only) |
| `make index` | Subset of Step 6 (code indexing only) |
| `make status` | Quick tool status check |
</related>
