---
name: impact-analysis
description: Analyzes change impact before code modifications to prevent regression
version: 3.0.0
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
trigger: "Before ANY code modification or refactoring"
---

## Quick Reference
- **필수**: 모든 파일 수정 전 실행 (신규 standalone 파일 제외)
- **스크립트**: `python3 scripts/find_dependents.py <file>`
- **Grep 패턴**: `from {module} import|import {module}` (의존성 추적)
- **Impact score**: 1-10, score > 7이면 human approval 필요
- **Output**: JSON (target_files, impact_score, incoming_deps, outgoing_deps, warnings)

---

# Skill: Impact Analysis

> **Goal**: Prevent regression by understanding dependency chains before code changes.
> **Priority**: MANDATORY - Must be executed before any file modification.

---

## Prerequisites

- Python 3.12+ (`python3 --version`)
- `scripts/find_dependents.py` (프로젝트 내 포함)

---

## Procedure

### Step 1: Identify Targets
List the files you intend to modify.

```python
target_files = ["src/utils.py", "src/models.py"]
```

### Step 2: Run Impact Analysis
Grep과 Glob을 사용하여 의존성 체인을 분석한다.

**방법 1: 스크립트 사용 (권장)**
```bash
python3 scripts/find_dependents.py src/utils.py
python3 scripts/find_dependents.py src/models.py
```

**방법 2: 네이티브 도구 직접 사용**
```
# import/require 검색으로 의존성 추적
Grep(pattern: "from utils import|import utils", path: "src/", output_mode: "files_with_matches")
Grep(pattern: "from models import|import models", path: "src/", output_mode: "files_with_matches")

# 테스트 커버리지 확인
Grep(pattern: "utils|models", path: "tests/", output_mode: "files_with_matches")
```

### Step 3: Review Impact Report

Check the following areas in the report:

| Area | What to Look For |
|------|------------------|
| **Incoming Dependencies** | Who calls these files? |
| **Outgoing Dependencies** | What do these files call? |
| **High-Risk Warnings** | Circular dependencies, core API usage |
| **Test Coverage** | Which tests cover this code? |

### Step 4: Plan Mitigation
If high impact is detected:
1. Update `.gsd/STATE.md` to include verification steps
2. Add affected dependent modules to test scope
3. Consider incremental rollout strategy

---

## Compliance Rules

| Rule | Description |
|------|-------------|
| **Mandatory** | You MUST NOT skip this step for any file modification |
| **Exception** | New standalone files don't require analysis |
| **Escalation** | If impact score > 7, require human approval before proceeding |

---

## Output Format

```json
{
  "target_files": ["src/utils.py"],
  "impact_score": 5,
  "incoming_deps": ["src/api.py", "tests/test_utils.py"],
  "outgoing_deps": ["src/constants.py"],
  "warnings": [],
  "recommendation": "Safe to proceed with standard testing"
}
```

## Scripts

- `scripts/find_dependents.py`: Find files importing a target module. Calculates impact score (1-10) with escalation level. Output: JSON
