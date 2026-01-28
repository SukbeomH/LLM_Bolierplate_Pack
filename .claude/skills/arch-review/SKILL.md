---
name: arch-review
description: Validates architectural rules and ensures design quality
version: 2.0.0
allowed-tools:
  - query_code_graph
  - Read
trigger: "Before merging PRs or completing major features"
---

# Skill: Architecture Review

> **Goal**: Validate code changes against architectural rules and patterns.
> **Scope**: Uses code-graph-rag for architecture validation.

---

## Prerequisites

- Memgraph must be running (`docker compose up -d`)
- code-graph-rag MCP server must be configured in `.mcp.json`

---

## Procedure

### Step 1: Run Local Architecture Check
Use code-graph-rag to verify local structure compliance.

```
query_code_graph("check architecture layering violations in src/")
```

### Step 2: Verify Boundary Compliance
Cross-check against defined boundaries:

| Boundary | Check |
|----------|-------|
| Layer isolation | UI → Service → Repository only |
| Circular deps | No cycles in call graph |
| External calls | Only via approved adapters |

### Step 3: Generate Report
Compile findings into a structured report.

---

## Output Format

```json
{
  "status": "PASS | WARN | FAIL",
  "violations": [
    {
      "type": "layer_violation",
      "source": "src/ui/Dashboard.tsx",
      "target": "src/repository/UserRepo.py",
      "severity": "HIGH",
      "recommendation": "Add service layer"
    }
  ],
  "patterns_matched": ["repository-pattern", "facade-pattern"]
}
```

---

## Escalation Matrix

| Severity | Action |
|----------|--------|
| LOW | Log warning, proceed |
| MEDIUM | Require acknowledgment in DECISIONS.md |
| HIGH | Block and require human approval |
| CRITICAL | Stop all work, escalate to tech lead |
