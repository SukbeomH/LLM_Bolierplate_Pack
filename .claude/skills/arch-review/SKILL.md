---
name: arch-review
description: Validates architectural rules and ensures design quality
version: 3.0.0
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
trigger: "Before merging PRs or completing major features"
---

## Quick Reference
- **순환 import**: `python3 scripts/find_circular_imports.py`
- **복잡도 검사**: `bash scripts/check_complexity.sh`
- **레이어 검증**: UI → Service → Repository 순방향만 허용
- **Severity**: LOW (log), MEDIUM (DECISIONS.md 기록), HIGH (block), CRITICAL (stop)
- **Memory recall**: `.gsd/memories/architecture-decision/` 검색 후 일관성 확인

---

# Skill: Architecture Review

> **Goal**: Validate code changes against architectural rules and patterns.
> **Scope**: Uses Grep/Glob/Read 및 스크립트로 architecture validation 수행.

---

## Prerequisites

- Python 3.12+ (`python3 --version`)
- `scripts/check_complexity.sh`, `scripts/find_circular_imports.py` (프로젝트 내 포함)

---

## Pre-Review: Memory Recall

아키텍처 리뷰 전 과거 결정 사항을 recall하여 일관성을 검증한다:

```
Grep(pattern: "architecture|arch.*decision", path: ".gsd/memories/architecture-decision/", output_mode: "files_with_matches")
```

매칭된 파일을 Read하여 과거 `architecture-decision` 메모리와 현재 변경의 일관성을 확인.
결과가 부족하면 broader 검색:

```
Grep(pattern: "architecture|design.*pattern", path: ".gsd/memories/", output_mode: "files_with_matches")
```

---

## Procedure

### Step 1: Run Local Architecture Check
Grep/Glob을 사용하여 구조 검증:

```bash
# 순환 import 검출
python3 scripts/find_circular_imports.py

# 복잡도 검사
bash scripts/check_complexity.sh
```

```
# 레이어 위반 검출 (예: UI가 Repository를 직접 호출)
Grep(pattern: "from.*repository.*import|import.*repository", path: "src/ui/", output_mode: "files_with_matches")
Grep(pattern: "from.*ui.*import|import.*ui", path: "src/repository/", output_mode: "files_with_matches")
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

## Scripts

- `scripts/check_complexity.sh`: Check McCabe complexity, argument counts, and naming conventions via ruff
- `scripts/find_circular_imports.py`: Detect circular import dependencies using DFS cycle detection. Output: JSON
