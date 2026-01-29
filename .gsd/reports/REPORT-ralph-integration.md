# Ralph 패턴 통합 보고서

> 작성일: 2026-01-29
> 대상: GSD Boilerplate
> 수정: 2026-01-29 (컨텍스트 관리 전략 추가)

> **📌 구현 현황**: 본 문서의 "신규" 항목 중 다수가 구현 완료됨.
> 최신 구현 상태는 [REPORT-implementation-status-2026-01.md](./REPORT-implementation-status-2026-01.md) 참조.

---

## 개요

Ralph의 자율 루프 패턴을 현재 GSD Boilerplate에 통합할 경우의 변경 사항과 예상 결과를 분석한다.

---

## 핵심 설계 원칙: 컨텍스트 관리

### 문제 인식

Ralph 원본 철학과 파일 축적 간의 충돌:

| Ralph 원칙 | 단순 적용 시 문제 |
|-----------|------------------|
| "Fresh context each iteration" | JOURNAL.md 축적 → 컨텍스트 증가 |
| "Git is memory, not context window" | 매번 prd.json + progress.txt 읽기 → 컨텍스트 소비 |
| "One context, one goal" | 패턴 섹션 + 히스토리 → 목표 희석 |

### 예상 컨텍스트 증가량 (미관리 시)

```
세션 1:  JOURNAL.md ~2KB,  prd.json ~1KB  →  ~3KB
세션 10: JOURNAL.md ~20KB, prd.json ~3KB  →  ~23KB
세션 30: JOURNAL.md ~60KB, prd.json ~5KB  →  ~65KB  ⚠️ 위험
```

### 해결책: 2-레이어 분리 구조

```
.gsd/
├── PATTERNS.md              # 핵심 패턴만 (최대 2KB, 20항목) ← 매번 읽음
├── CURRENT.md               # 현재 세션 컨텍스트만 (~1KB) ← 매번 읽음
├── prd-active.json          # pending 작업만 (~3KB) ← 매번 읽음
│
├── prd-done.json            # completed 작업 ← 읽지 않음
├── JOURNAL.md               # 최근 5개 세션만 ← 읽지 않음
├── CHANGELOG.md             # 최근 변경사항만 ← 필요시에만
│
├── reports/                 # 분석/조사 보고서 ← 필요시에만
│   ├── REPORT-ralph-integration.md
│   └── REPORT-ralph-usecases-scenarios.md
│
├── research/                # 리서치 문서 ← 필요시에만
│   └── RESEARCH-*.md
│
└── archive/                 # 장기 보관 ← 읽지 않음
    ├── journal-2026-01.md
    ├── prd-2026-01.json
    └── changelog-2026-01.md
```

### 컨텍스트 예산

**항상 읽음 (Active Layer)**

| 파일 | 크기 제한 | 읽기 시점 | 목적 |
|------|----------|----------|------|
| PATTERNS.md | **2KB** (20항목) | 매 세션 시작 | 핵심 학습 |
| CURRENT.md | **1KB** | 현재 세션 | 현재 작업 컨텍스트 |
| prd-active.json | **3KB** | 작업 선택 시 | 다음 작업 결정 |
| **합계** | **~6KB** | **고정** | |

**읽지 않음 (Archive Layer)**

| 파일/폴더 | 용도 | 읽기 시점 |
|-----------|------|----------|
| JOURNAL.md | 세션 히스토리 | 디버깅 시에만 |
| CHANGELOG.md | 변경 이력 | 릴리스 시에만 |
| prd-done.json | 완료 기록 | 감사 시에만 |
| reports/ | 분석 보고서 | 의사결정 시에만 |
| research/ | 리서치 문서 | 참조 필요시에만 |
| archive/ | 장기 보관 | 거의 읽지 않음 |

### 자동 정리 규칙

```yaml
# .gsd/context-config.yaml
compaction:
  patterns_max_items: 20
  patterns_max_kb: 2
  journal_keep_sessions: 5
  changelog_keep_entries: 20
  prd_archive_completed: true
  auto_archive_on_session_end: true

folders:
  reports: reports/          # REPORT-*.md 자동 이동
  research: research/        # RESEARCH-*.md 자동 이동
  archive: archive/          # 월별 아카이브

archive_schedule:
  journal: monthly           # journal-YYYY-MM.md
  changelog: monthly         # changelog-YYYY-MM.md
  prd_done: monthly          # prd-YYYY-MM.json
```

---

## 권장 사항 1: progress.txt 패턴을 JOURNAL.md에 적용

### 현재 상태

**JOURNAL.md (현재)**
```markdown
### [Session YYYY-MM-DD HH:MM]
- **Duration**: {time}
- **Phase**: {current phase}
- **Accomplished**: {what was done}
- **Blockers**: {any issues}
- **Next**: {planned next steps}
```

**Ralph progress.txt**
```markdown
## Codebase Patterns  ← 상단 고정 섹션
- Use `sql<number>` template for aggregations
- Always use `IF NOT EXISTS` for migrations

## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
```

### 변경 내용 (컨텍스트 관리 반영)

| 파일 | 변경 유형 | 상세 내용 |
|------|----------|----------|
| `.gsd/PATTERNS.md` | **신규** | 핵심 패턴 전용 파일 (2KB 제한, 20항목) |
| `.gsd/JOURNAL.md` | 역할 변경 | 아카이브용 (최근 5개 세션만, 읽지 않음) |
| `.gsd/archive/` | **신규** | 오래된 세션 엔트리 보관 |
| `.claude/skills/executor/SKILL.md` | 로직 추가 | PATTERNS.md 업데이트 + JOURNAL.md 아카이빙 |
| `scripts/compact-context.sh` | **신규** | 자동 정리 스크립트 |

### 변경 후 파일 구조

**PATTERNS.md** (매 세션 읽음, 2KB 제한)
```markdown
# Codebase Patterns
<!-- 최대 20개 항목, 2KB 제한. 오래된 항목은 자동 제거 -->

## Architecture
- jose > jsonwebtoken (Edge runtime 호환)
- User model: prisma/schema.prisma:45

## Gotchas
- httpOnly 쿠키는 localhost에서도 HTTPS 필요
- migration 전 prisma generate 필수

## Conventions
- API route: src/app/api/{resource}/route.ts
- 테스트: tests/{resource}_test.py
```

**JOURNAL.md** (아카이브용, 읽지 않음)
```markdown
# Session Archive
<!-- 최근 5개 세션만 유지. 오래된 엔트리는 archive/로 이동 -->

### [Session 2026-01-29 14:30]
- **Phase**: 2.1 - API Implementation
- **Accomplished**: Login endpoint completed
- **Files Changed**: src/app/api/auth/login/route.ts, prisma/schema.prisma
- **Learnings**: (PATTERNS.md로 추출됨)
- **Next**: Session management 구현
```

### 예상 결과

| 측면 | Before | After |
|------|--------|-------|
| **패턴 접근성** | 각 세션 로그 순회 | PATTERNS.md 직접 읽기 |
| **컨텍스트 소비** | 무제한 증가 | **고정 2KB** |
| **세션 간 학습** | 암묵적 | 명시적 (PATTERNS.md) |
| **Fresh 세션 효율** | 매번 탐색 필요 | 즉시 컨텍스트 확보 |
| **컨텍스트 복구 시간** | 평균 5-10분 | **예상 30초** |
| **반복 실수** | 빈번 | 감소 (Gotchas 섹션) |

### 구현 난이도

- **난이도**: 낮음
- **예상 작업**:
  - PATTERNS.md 템플릿 생성
  - executor skill에 패턴 추출 로직 (~15줄)
  - compact-context.sh 스크립트 (~30줄)
- **위험도**: 낮음 (기존 기능 영향 없음)

---

## 권장 사항 2: prd.json 형식을 planner skill에 추가

### 현재 상태

**planner skill 출력**: PLAN.md (마크다운 + YAML frontmatter)
**Ralph 출력**: prd.json (JSON 구조)

### 변경 내용 (컨텍스트 관리 반영)

| 파일 | 변경 유형 | 상세 내용 |
|------|----------|----------|
| `.claude/skills/planner/SKILL.md` | 옵션 추가 | `--format json` 플래그로 prd.json 출력 지원 |
| `.gsd/prd-active.json` | **신규** | pending 작업만 (~3KB 제한) |
| `.gsd/prd-done.json` | **신규** | completed 작업 (읽지 않음, 기록용) |
| `.claude/skills/executor/SKILL.md` | 로직 추가 | 완료 시 active→done 이동 |

### 변경 후 planner 출력 옵션

```
/plan "User authentication feature"           # 기본: PLAN.md 출력
/plan "User authentication feature" --json    # 추가: prd-active.json 출력
```

### prd-active.json 구조 (pending만, 매 세션 읽음)

```json
{
  "project": "GSD Project",
  "branchName": "feature/user-auth",
  "description": "User Authentication Feature",
  "phase": 2,
  "tasks": [
    {
      "id": "T-001",
      "plan": "2.1",
      "title": "Add User model to database",
      "acceptanceCriteria": [
        "User table with email, password_hash columns",
        "Migration runs successfully",
        "uv run mypy passes"
      ],
      "priority": 1,
      "status": "pending"
    }
  ]
}
```

### prd-done.json 구조 (completed, 읽지 않음)

```json
{
  "completed": [
    {
      "id": "T-000",
      "title": "Initialize project structure",
      "completedAt": "2026-01-28T10:30:00Z",
      "commit": "abc1234"
    }
  ]
}
```

### 예상 결과

| 측면 | Before | After |
|------|--------|-------|
| **상태 추적** | STATE.md (수동 갱신) | prd-active.json (자동 갱신) |
| **컨텍스트 소비** | 무제한 증가 | **고정 ~3KB** (pending만) |
| **작업 완료 판단** | 사람이 PLAN.md 확인 | `jq '.tasks | length' prd-active.json` → 0이면 완료 |
| **자동화 가능성** | 낮음 | 높음 (JSON 파싱 용이) |
| **외부 도구 연동** | 어려움 | 쉬움 (CI/CD, 대시보드) |
| **완료 조건 명확성** | 암묵적 | 명시적 (prd-active.json 비어있으면 완료) |

### 구현 난이도

- **난이도**: 중간
- **예상 작업**:
  - planner skill에 JSON 출력 로직 추가 (~50줄)
  - executor에 active→done 이동 로직 추가 (~40줄)
  - 월별 prd-done.json 아카이빙 (~20줄)
- **위험도**: 낮음 (선택적 기능, 기존 워크플로우 유지)

---

## 권장 사항 3: 자율 루프를 executor skill에 통합

### 현재 상태

**executor skill**: 단일 PLAN.md 실행 후 종료
**Ralph**: bash 루프가 반복적으로 fresh 인스턴스 생성

### 변경 내용

| 파일 | 변경 유형 | 상세 내용 |
|------|----------|----------|
| `scripts/gsd-loop.sh` | 신규 생성 | Ralph 스타일 자율 루프 스크립트 |
| `.claude/skills/executor/SKILL.md` | 출력 추가 | 완료 시그널 `<gsd>COMPLETE</gsd>` 반환 |
| `.gsd/LOOP-CONFIG.md` | 신규 생성 | 루프 설정 (max_iterations, auto_archive 등) |
| `context-health-monitor` | 연동 | 컨텍스트 임계치 도달 시 자동 덤프 후 루프 재시작 |

### gsd-loop.sh 설계

```bash
#!/bin/bash
# GSD Loop - Ralph-style autonomous execution

MAX_ITERATIONS=${1:-10}
TOOL="claude"

for i in $(seq 1 $MAX_ITERATIONS); do
  echo "=== GSD Iteration $i of $MAX_ITERATIONS ==="

  # prd-active.json에서 다음 pending 작업 확인
  NEXT_TASK=$(jq -r '.tasks[] | select(.status=="pending") | .id' .gsd/prd-active.json | head -1)

  if [ -z "$NEXT_TASK" ]; then
    echo "All tasks complete!"
    exit 0
  fi

  # Fresh Claude 인스턴스로 실행
  OUTPUT=$(claude --print "/execute $NEXT_TASK" 2>&1 | tee /dev/stderr) || true

  # 완료 시그널 확인
  if echo "$OUTPUT" | grep -q "<gsd>COMPLETE</gsd>"; then
    echo "GSD Loop: All phases complete!"
    exit 0
  fi

  sleep 2
done

echo "Max iterations reached. Check .gsd/prd.json for status."
```

### 예상 결과

| 측면 | Before | After |
|------|--------|-------|
| **실행 모델** | 수동 `/execute` 호출 | 자동 루프 (`./scripts/gsd-loop.sh`) |
| **컨텍스트 소진** | 세션 종료 필요 | 자동 fresh 인스턴스 |
| **야간 작업** | 불가 | 가능 (무인 실행) |
| **대규모 작업** | 컨텍스트 한계 | 무제한 (반복 생성) |
| **완료 판단** | 사람이 확인 | 자동 (`<gsd>COMPLETE</gsd>`) |
| **실패 복구** | 수동 | 자동 (다음 반복에서 재시도) |

### 컨텍스트 흐름도

```
┌─────────────────────────────────────────────────────────┐
│                     gsd-loop.sh                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Iteration 1                                     │   │
│  │  - Read prd.json → T-001 pending                │   │
│  │  - Spawn Claude: /execute T-001                 │   │
│  │  - Claude: implements, commits, updates prd.json│   │
│  │  - Exit (no COMPLETE signal)                    │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Iteration 2 (Fresh Context)                    │   │
│  │  - Read prd.json → T-001 done, T-002 pending   │   │
│  │  - Spawn Claude: /execute T-002                 │   │
│  │  - ...                                          │   │
│  └─────────────────────────────────────────────────┘   │
│                         ↓                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Iteration N                                    │   │
│  │  - All tasks status=completed                   │   │
│  │  - Claude returns <gsd>COMPLETE</gsd>           │   │
│  │  - Loop exits successfully                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 구현 난이도

- **난이도**: 높음
- **예상 작업**:
  - `scripts/gsd-loop.sh` 작성 (~100줄)
  - executor skill 완료 시그널 추가 (~20줄)
  - context-health-monitor 연동 (~50줄)
  - prd.json ↔ STATE.md 동기화 로직 (~50줄)
- **위험도**: 중간 (기존 수동 워크플로우는 유지되나, 자동화 로직 버그 시 무한 루프 가능)

---

## 통합 로드맵

### Phase 1: 즉시 (1-2일)

| 작업 | 파일 | 우선순위 |
|------|------|----------|
| JOURNAL.md에 Codebase Patterns 섹션 추가 | `.gsd/JOURNAL.md` | 필수 |
| executor에 Learnings 기록 로직 추가 | `.claude/skills/executor/SKILL.md` | 필수 |

**예상 효과**: 세션 간 학습 즉시 개선

### Phase 2: 단기 (1주)

| 작업 | 파일 | 우선순위 |
|------|------|----------|
| planner에 `--json` 옵션 추가 | `.claude/skills/planner/SKILL.md` | 권장 |
| prd.json 스키마 정의 | `.gsd/schemas/prd.schema.json` | 권장 |
| executor에 prd.json 상태 업데이트 | `.claude/skills/executor/SKILL.md` | 권장 |

**예상 효과**: 자동화 기반 마련

### Phase 3: 장기 (2-3주)

| 작업 | 파일 | 우선순위 |
|------|------|----------|
| gsd-loop.sh 작성 | `scripts/gsd-loop.sh` | 선택 |
| 완료 시그널 추가 | `.claude/skills/executor/SKILL.md` | 선택 |
| context-health-monitor 연동 | `.claude/skills/context-health-monitor/SKILL.md` | 선택 |
| 자동 아카이빙 | `scripts/gsd-archive.sh` | 선택 |

**예상 효과**: 완전 자율 실행 가능

---

## 위험 및 완화

| 위험 | 영향도 | 완화 방안 |
|------|--------|----------|
| 자율 루프 무한 실행 | 높음 | max_iterations 제한, 3회 연속 실패 시 중단 |
| prd.json ↔ PLAN.md 불일치 | 중간 | 단일 소스 원칙: prd-active.json이 마스터 |
| 패턴 섹션 오염 | 낮음 | "general and reusable" 가이드라인 + 20항목 제한 |
| 기존 워크플로우 충돌 | 낮음 | 모든 변경은 선택적 (기본값 유지) |
| **컨텍스트 무한 증가** | **높음** | **2-레이어 분리 + 자동 아카이빙** |
| **PATTERNS.md 크기 초과** | 중간 | 2KB 하드 제한 + 오래된 항목 자동 제거 |
| **아카이브 누락** | 낮음 | SessionEnd 훅에서 자동 실행 |

---

## 결론

### 권장 사항 1 (progress.txt → JOURNAL.md)
- **적용 권장**: 즉시
- **ROI**: 높음 (최소 변경으로 최대 효과)
- **이유**: 세션 간 학습 품질 즉시 향상

### 권장 사항 2 (prd.json 형식)
- **적용 권장**: 단기
- **ROI**: 중간 (자동화 기반 구축)
- **이유**: 외부 도구 연동 및 CI/CD 파이프라인 통합 용이

### 권장 사항 3 (자율 루프)
- **적용 권장**: 검증 후 장기
- **ROI**: 높음 (무인 실행 가능)
- **이유**: 복잡도 높으나, 대규모 작업에서 생산성 극대화

---

## 부록: 파일 변경 요약 (컨텍스트 관리 반영)

```
.gsd/
├── PATTERNS.md             # 신규: 핵심 패턴 (2KB 제한, 매번 읽음)
├── CURRENT.md              # 신규: 현재 세션 컨텍스트 (1KB)
├── prd-active.json         # 신규: pending 작업만 (3KB 제한)
│
├── prd-done.json           # 신규: completed 기록 (읽지 않음)
├── JOURNAL.md              # 변경: 최근 5개 세션만 (읽지 않음)
├── CHANGELOG.md            # 변경: 최근 20개 엔트리만 (필요시에만)
├── context-config.yaml     # 신규: 정리 규칙
├── LOOP-CONFIG.md          # 신규 (Phase 3)
│
├── reports/                # 신규: 분석/조사 보고서 폴더
│   ├── REPORT-ralph-integration.md
│   └── REPORT-ralph-usecases-scenarios.md
│
├── research/               # 신규: 리서치 문서 폴더
│   └── RESEARCH-*.md
│
├── schemas/
│   └── prd.schema.json     # 신규 (Phase 2)
│
└── archive/                # 월별 아카이브
    ├── journal-YYYY-MM.md
    ├── changelog-YYYY-MM.md
    └── prd-YYYY-MM.json

.claude/skills/
├── executor/SKILL.md       # 수정 (PATTERNS.md 추출, prd 분리)
├── planner/SKILL.md        # 수정 (--json 옵션)
└── context-health-monitor/SKILL.md  # 수정 (루프 연동, 자동 정리)

scripts/
├── gsd-loop.sh             # 신규 (Phase 3)
├── compact-context.sh      # 신규: 컨텍스트 자동 정리
├── organize-docs.sh        # 신규: reports/, research/ 자동 정리
└── gsd-archive.sh          # 신규 (Phase 3)
```

### 컨텍스트 예산 요약

**Active Layer (항상 읽음)**

| 파일 | 크기 | 빈도 |
|------|------|------|
| PATTERNS.md | 2KB | 매 세션 |
| CURRENT.md | 1KB | 매 세션 |
| prd-active.json | 3KB | 매 세션 |
| **총합** | **~6KB** | **고정** |

**Archive Layer (읽지 않음)**

| 파일/폴더 | 용도 |
|-----------|------|
| JOURNAL.md | 세션 히스토리 |
| CHANGELOG.md | 변경 이력 |
| prd-done.json | 완료 기록 |
| reports/ | 분석 보고서 |
| research/ | 리서치 문서 |
| archive/ | 장기 보관 |
