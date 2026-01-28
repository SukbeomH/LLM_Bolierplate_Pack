---
researched_at: 2026-01-28
discovery_level: 3
---

# everything-claude-code 분석 및 보일러플레이트 비교

## Objective

everything-claude-code 저장소를 심층 분석하고, 현재 보일러플레이트와 아키텍처/기능/철학 수준에서 비교한다.

## Discovery Level

**Level 3** -- 심층 비교 분석 + 갭 식별 + 채택 권고

---

## 1. everything-claude-code 개요

**저자**: Affaan Mustafa (@affaanmustafa) -- Anthropic x Forum Ventures 해커톤 우승자
**성격**: Claude Code 파워유저를 위한 **프로덕션 검증** 설정 컬렉션
**배포**: Claude Code Plugin 마켓플레이스 설치 지원
**라이선스**: MIT

### 핵심 구성

| 항목 | 수량 |
|------|------|
| Agents (서브에이전트) | 12 |
| Skills | 15+ |
| Commands (슬래시 명령) | 23+ |
| Rules (모듈형 규칙) | 8 |
| Hooks (이벤트 자동화) | 16 |
| MCP Configs | 14 |
| Contexts (동적 프롬프트) | 3 |
| Scripts (Node.js) | 6+ |

### 디렉토리 구조

```
everything-claude-code/
├── agents/              # 12 서브에이전트 (YAML frontmatter + markdown)
├── skills/              # 15+ 도메인별 스킬
├── commands/            # 23+ 슬래시 명령
├── rules/               # 8 모듈형 규칙 파일
├── hooks/               # 이벤트 기반 자동화 스크립트
├── contexts/            # 동적 시스템 프롬프트 (dev/review/research)
├── examples/            # 참조 설정 (CLAUDE.md 예시, 세션 파일)
├── mcp-configs/         # 14 MCP 서버 정의
├── scripts/             # Node.js 유틸리티 (398줄 lib/utils.js)
├── tests/               # 테스트 슈트
├── plugins/             # 플러그인 문서
├── assets/              # 이미지 (가이드용)
├── .claude-plugin/      # 플러그인 메타데이터 (plugin.json)
├── the-shortform-guide.md   # 셋업 기초 가이드
└── the-longform-guide.md    # 고급 패턴 & 최적화
```

---

## 2. 아키텍처 비교

### 2.1 프로젝트 성격

| | **보일러플레이트** | **everything-claude-code** |
|---|---|---|
| **유형** | 개발 인프라 + GSD 방법론 템플릿 | Claude Code 설정 컬렉션 + 가이드 |
| **산출물** | SPEC -> PLAN -> 코드 -> 검증 사이클 | 에이전트/스킬/후크/규칙 설정 파일 |
| **대상** | Python 프로젝트 + AI 에이전트 개발 | 모든 언어/프레임워크의 Claude Code 사용자 |
| **언어** | Python 3.11+ (uv) | JavaScript/TypeScript (Node.js 스크립트) |
| **배포** | git clone + make setup | Plugin marketplace 또는 수동 복사 |
| **문서** | 한국어/영어 이중 | 영어 단일 |

### 2.2 기능 매트릭스

| 영역 | **보일러플레이트** | **everything-claude-code** | 비고 |
|---|---|---|---|
| **워크플로우 명령** | 29 (GSD) | 23+ (개발 중심) | 보일러플레이트가 방법론 더 체계적 |
| **에이전트 스킬** | 14 | 15+ | 유사 수준, 도메인 다름 |
| **서브에이전트** | 0 (직접 실행) | 12 (모델별 분리) | **격차: 서브에이전트 아키텍처** |
| **모듈형 규칙** | 0 (CLAUDE.md 통합) | 8 (분리 파일) | **격차: 규칙 모듈화** |
| **후크 시스템** | 0 | 16 (6종 이벤트) | **격차: 후크 자동화** |
| **동적 컨텍스트** | 0 | 3 (dev/review/research) | **격차: 컨텍스트 전환** |
| **MCP 통합** | 3 (graph-code, memorygraph, context7) | 14 (GitHub, Vercel, Supabase 등) | 보일러플레이트는 RAG 특화 |
| **GSD 방법론** | 완전 (SPEC/PLAN/EXECUTE/VERIFY) | 없음 (자체 워크플로우) | **강점: GSD 체계** |
| **문서 템플릿** | 22 | 0 | **강점: 템플릿 라이브러리** |
| **인프라 자동화** | Docker + Makefile (17 타겟) | 없음 | **강점: 인프라** |
| **CI/CD** | GitHub Actions (1 workflow) | 없음 | 유사 |
| **테스트** | 8 (Python, pytest) | 있음 (Node.js) | 유사 |
| **멀티 에이전트** | 3 (Claude/GitHub/Gemini) | 1 (Claude Code only) | **강점: 멀티 에이전트** |
| **지속적 학습** | memory-graph MCP | 세션 후크 + 패턴 추출 | 접근 방식 다름 |
| **플러그인 배포** | 없음 | Claude Code Plugin 지원 | **격차: 배포 시스템** |

### 2.3 에이전트/스킬 비교

#### 보일러플레이트 14 스킬

| 카테고리 | 스킬 | 모델 |
|----------|------|------|
| Planning | planner, plan-checker | 미지정 (호스트 모델) |
| Execution | executor, commit, create-pr, clean | 미지정 |
| Verification | verifier, empirical-validation, pr-review | 미지정 |
| Analysis | arch-review, impact-analysis, codebase-mapper, context-health-monitor, debugger | 미지정 |

#### everything-claude-code 12 에이전트

| 카테고리 | 에이전트 | 모델 |
|----------|---------|------|
| Planning | planner, architect | Opus |
| Development | tdd-guide | Opus |
| Review | code-reviewer, security-reviewer, go-reviewer, database-reviewer | Opus |
| Build | build-error-resolver, go-build-resolver | Haiku |
| Maintenance | refactor-cleaner, doc-updater | Haiku |
| Testing | e2e-runner | Opus |

**핵심 차이**: everything-claude-code는 **모델별 비용 최적화** (Opus/Haiku 분리), 보일러플레이트는 **GSD 사이클 매핑** (Planning->Execution->Verification->Analysis)

---

## 3. 핵심 격차 분석 (Gap Analysis)

### 3.1 서브에이전트 아키텍처 (Critical Gap)

**현재**: 보일러플레이트의 14 스킬은 모두 **호스트 모델에서 직접 실행**. 모델 선택 불가.

**everything-claude-code**: 12 에이전트가 **YAML frontmatter로 모델 지정** + **도구 제한**.

```yaml
# everything-claude-code 에이전트 예시
---
name: build-error-resolver
model: haiku
tools: [Bash, Read, Grep, Glob]
---
```

**영향**: 비용 최적화 불가 (탐색에 Opus 사용 = 낭비), 도구 범위 제한 불가

**권고**: 높은 추론이 필요한 스킬(arch-review, planner)은 Opus, 단순 실행(clean, commit)은 Haiku 지정 검토

### 3.2 후크 시스템 (High Gap)

**현재**: 후크 없음. 모든 검증은 수동 명령 또는 GSD 워크플로우 의존.

**everything-claude-code 후크 (16개)**:

| 이벤트 | 후크 | 효과 |
|--------|------|------|
| PreToolUse | tmux 강제, .md 생성 차단, git push 리뷰 | 실수 사전 방지 |
| PostToolUse | Prettier 자동 포맷, TypeScript 체크, console.log 경고 | 즉시 품질 피드백 |
| SessionStart | 이전 컨텍스트 로드, 패키지 매니저 감지 | 세션 연속성 |
| SessionEnd | 상태 저장, 패턴 평가 | 학습 지속성 |
| PreCompact | 상태 백업 | 컨텍스트 손실 방지 |
| Stop | console.log 최종 체크 | 배포 안전 |

**권고**: 단계적 도입. 우선순위:
1. **SessionStart**: `.gsd/STATE.md` 자동 로드 (GSD /resume 자동화)
2. **PreToolUse (Bash)**: `uv run ruff check` / `uv run mypy` 자동 트리거
3. **PostToolUse (Write/Edit)**: Python 파일 변경 시 ruff 자동 포맷
4. **PreCompact**: STATE.md 자동 저장

### 3.3 모듈형 규칙 (Medium Gap)

**현재**: 모든 규칙이 `CLAUDE.md` 단일 파일에 통합 (80줄).

**everything-claude-code**: 8개 독립 규칙 파일

| 파일 | 내용 |
|------|------|
| `security.md` | 시크릿, 입력 검증, SQL injection, XSS, CSRF, rate limiting |
| `coding-style.md` | 불변성, 파일 크기, 에러 핸들링, Zod 검증 |
| `testing.md` | 80% 커버리지, TDD 필수, E2E 크리티컬 플로우 |
| `git-workflow.md` | conventional commits, feature 워크플로우, PR 규칙 |
| `agents.md` | 에이전트 오케스트레이션, 자동 트리거 조건 |
| `patterns.md` | API 응답 포맷, Repository 패턴, Service 레이어 |
| `performance.md` | 모델 선택, 컨텍스트 윈도우 관리 |

**장점**: 규칙별 독립 업데이트, 프로젝트별 선택적 적용, 관심사 분리
**권고**: `CLAUDE.md`가 비대해지면 규칙 모듈화 검토. 현재 80줄은 관리 가능 수준이므로 즉시 필요하지 않음.

### 3.4 동적 컨텍스트 전환 (Low Gap)

**현재**: 단일 모드 (CLAUDE.md 항상 적용)

**everything-claude-code**: 3개 컨텍스트 (dev/review/research) CLI 플래그로 전환

```bash
claude --system-prompt "$(cat ~/.claude/contexts/dev.md)"
```

**권고**: 보일러플레이트는 GSD 워크플로우가 이 역할을 대체 (/execute = dev, /verify = review, /research-phase = research). 별도 컨텍스트 파일은 불필요.

### 3.5 지속적 학습 메커니즘 비교

| | **보일러플레이트** | **everything-claude-code** |
|---|---|---|
| **저장소** | memory-graph MCP (그래프 DB) | 파일 시스템 (~/.claude/sessions/) |
| **트리거** | 수동 (`store_memory`, `recall_memories`) | 자동 (SessionEnd 후크) |
| **형태** | 구조화된 메모리 노드 + 관계 | 패턴 추출 → 스킬 파일 |
| **범위** | 프로젝트 내 + 크로스 프로젝트 (도메인) | 세션 내 → 스킬로 승격 |
| **진화** | 정적 (저장/조회) | 동적 (instinct → skill → agent 진화) |

**보일러플레이트 강점**: 구조화된 그래프 기반 메모리, 관계 추적, 크로스 프로젝트 도메인
**everything-claude-code 강점**: 자동 추출, 진화 메커니즘, 세션 연속성

---

## 4. 철학 비교

### 4.1 개발 방법론

| | **보일러플레이트** | **everything-claude-code** |
|---|---|---|
| **접근** | 문서 중심 (SPEC -> PLAN -> 코드) | 에이전트 중심 (Plan -> TDD -> Review) |
| **계획** | GSD SPEC.md 작성 후 락 | /plan 명령 → planner agent |
| **실행** | 페이즈 기반 원자적 커밋 | TDD 사이클 (RED -> GREEN -> IMPROVE) |
| **검증** | 경험적 증거 기반 (VERIFICATION.md) | 체크포인트 기반 eval + E2E |
| **반복** | 3회 실패 → 접근 변경 | Continuous eval loop |

### 4.2 토큰 경제학

| | **보일러플레이트** | **everything-claude-code** |
|---|---|---|
| **모델 전략** | 단일 모델 (호스트) | 3-tier (Haiku/Sonnet/Opus) |
| **MCP 관리** | 3개 항상 활성 | 10개 미만 권장, 80 도구 상한 |
| **컨텍스트** | 무제한 (자동 요약) | 200k 중 70k 가용, 마지막 20% 회피 |
| **최적화** | GSD 문서로 컨텍스트 공유 | MCP → CLI+스킬 대체, mgrep 사용 |
| **패칭** | `make patch-prompt` (~50% 절감) | 없음 |

### 4.3 보안 접근

| | **보일러플레이트** | **everything-claude-code** |
|---|---|---|
| **규칙** | CLAUDE.md Agent Boundaries | rules/security.md (독립 파일) |
| **검증** | 수동 (.env 비커밋 규칙) | security-reviewer 에이전트 자동 트리거 |
| **범위** | .env, 시크릿 커밋 금지 | OWASP 전체 (SQLi, XSS, CSRF, Rate Limit) |
| **TLS** | SSL_CERT_FILE 지원 | 없음 |

---

## 5. 보일러플레이트 고유 강점

everything-claude-code에 **없는** 보일러플레이트 기능:

| 기능 | 상세 |
|------|------|
| **GSD 방법론** | SPEC -> PLAN -> EXECUTE -> VERIFY 전체 사이클. 29개 워크플로우 |
| **문서 템플릿 22개** | SPEC, PLAN, VERIFICATION, DEBUG, milestone, sprint 등 |
| **code-graph-rag** | Tree-sitter + Memgraph AST 분석. 리팩토링 전 영향도 분석 |
| **memory-graph** | 그래프 기반 영구 기억. 관계 추적, 도메인 분리 |
| **멀티 에이전트** | Claude Code + GitHub Agent + Gemini 동시 지원 |
| **인프라 자동화** | Docker Compose + Makefile 17 타겟 + make setup 원커맨드 |
| **시스템 프롬프트 패치** | make patch-prompt (~50% 토큰 절감) |
| **VS Code 팀 설정** | 워크스페이스 설정 + 확장 권장 공유 |
| **코드 품질 엄격** | Ruff 9종 + McCabe<=10 + max-args=6 + mypy strict |

---

## 6. 채택 권고

### 6.1 즉시 도입 (High Priority)

| # | 요소 | 현재 상태 | 도입 방안 | 효과 |
|---|------|-----------|-----------|------|
| 1 | **후크 시스템 기초** | 없음 | `.claude/settings.local.json`에 hooks 설정. SessionStart에서 STATE.md 로드, PostToolUse(Write/Edit)에서 ruff 자동 포맷 | 수동 /resume 불필요, 코드 품질 자동 보장 |
| 2 | **에이전트 모델 분리** | 14 스킬 모두 호스트 모델 | 분석/계획 스킬(arch-review, planner, plan-checker)에 Opus, 실행 스킬(clean, commit, create-pr)에 Haiku 지정 | 비용 최적화 |
| 3 | **security-reviewer 에이전트** | 없음 (수동 규칙) | 커밋 전 자동 트리거되는 보안 검토 에이전트 추가 | 보안 사각지대 해소 |

### 6.2 중기 검토 (Medium Priority)

| # | 요소 | 현재 상태 | 도입 방안 | 효과 |
|---|------|-----------|-----------|------|
| 4 | **TDD 워크플로우** | /verify만 존재 | tdd-guide 스킬 추가 (RED->GREEN->IMPROVE 사이클) | 테스트 선행 개발 강제 |
| 5 | **PreCompact 후크** | 없음 | 자동 요약 전 STATE.md + JOURNAL.md 저장 | 컨텍스트 손실 방지 |
| 6 | **지속적 학습 자동화** | memory-graph 수동 사용 | SessionEnd 후크에서 패턴 추출 → memory-graph 자동 저장 | 학습 연속성 |
| 7 | **E2E 테스트 스킬** | 없음 | Playwright 기반 e2e-runner 스킬 추가 | 크리티컬 플로우 검증 |

### 6.3 불필요 / 보류

| 요소 | 사유 |
|------|------|
| **규칙 모듈화** | 현재 CLAUDE.md 80줄 -- 관리 가능 수준. 200줄 초과 시 분리 검토 |
| **동적 컨텍스트** | GSD 워크플로우가 동일 역할 수행 (/execute=dev, /verify=review) |
| **Node.js 스크립트** | Python 생태계와 불일치. 필요 시 Python으로 재구현 |
| **플러그인 배포** | 보일러플레이트는 프로젝트 템플릿이므로 git clone이 적합 |
| **14 MCP 설정** | 보일러플레이트의 3 MCP (RAG 특화)가 목적에 부합. 불필요한 MCP 추가는 컨텍스트 낭비 |
| **Immutability 규칙** | TypeScript/React 패턴. Python에서는 해당 없음 |
| **Zod 입력 검증** | TypeScript 전용. Python은 Pydantic/TypedDict 사용 |
| **Go 관련 에이전트** | Go 미사용 |

---

## 7. 패턴 학습 (Patterns to Follow)

### 7.1 프로액티브 에이전트 트리거

everything-claude-code의 핵심 철학: **사용자가 요청하기 전에 에이전트가 먼저 실행**

```
복잡한 기능 → planner 자동 실행 (사용자 확인 대기)
코드 작성 완료 → code-reviewer 자동 실행
버그 수정 → tdd-guide 자동 실행
아키텍처 결정 → architect 자동 실행
```

GSD 적용: /execute 시 코드 작성 후 자동으로 /quick-check 트리거 검토

### 7.2 3-Tier 모델 전략

| 작업 | 모델 | 비용 |
|------|------|------|
| 탐색, 검색, 단순 편집 | Haiku | 1x |
| 멀티파일 구현, 오케스트레이션 | Sonnet | 5x |
| 복잡한 아키텍처, 보안 분석 | Opus | 15x |

### 7.3 Strategic Compaction

everything-claude-code는 컨텍스트 윈도우의 마지막 20%에 도달하면 **수동 컴팩션**을 권장. 자동 요약보다 선택적 보존이 효과적.

보일러플레이트의 context-health-monitor 스킬이 유사한 역할을 하지만, 후크 기반 자동 트리거로 강화 가능.

### 7.4 Iterative Retrieval Pattern

서브에이전트 반환값을 오케스트레이터가 매번 평가 → 후속 질문 → 최대 3회 반복

```
Orchestrator → Sub-agent: "Find auth implementation"
Sub-agent → Result
Orchestrator: "Which middleware handles JWT validation?"
Sub-agent → Refined Result
Orchestrator: Sufficient → Accept
```

---

## 8. Anti-Patterns to Avoid

| 패턴 | 사유 |
|------|------|
| **14 MCP 동시 활성** | 컨텍스트 윈도우 200k 중 70k만 가용. 보일러플레이트의 3 MCP가 효율적 |
| **Node.js 후크 스크립트** | Python 프로젝트에 Node.js 의존성 추가는 복잡성 증가. Python 또는 셸 스크립트 권장 |
| **console.log 후크** | Python 프로젝트에 해당 없음. print 문 제거는 ruff 규칙으로 대체 가능 |
| **Prettier 후크** | Python은 ruff format 사용 |
| **과도한 에이전트 분리** | 12 에이전트는 풀스택 JS/TS 프로젝트 기준. Python 보일러플레이트는 14 스킬 + 핵심 에이전트 2-3개가 적절 |

---

## 9. 종합 평가

### 9.1 요약

| 축 | 보일러플레이트 | everything-claude-code |
|---|---|---|
| **방법론 체계** | ★★★★★ | ★★☆☆☆ |
| **문서 템플릿** | ★★★★★ | ★☆☆☆☆ |
| **코드 분석 (RAG)** | ★★★★★ | ☆☆☆☆☆ |
| **에이전트 기억** | ★★★★☆ | ★★★☆☆ |
| **인프라 자동화** | ★★★★☆ | ☆☆☆☆☆ |
| **후크/자동화** | ☆☆☆☆☆ | ★★★★★ |
| **서브에이전트** | ☆☆☆☆☆ | ★★★★★ |
| **토큰 최적화** | ★★★☆☆ | ★★★★★ |
| **보안 자동화** | ★★☆☆☆ | ★★★★☆ |
| **배포/공유** | ★★☆☆☆ | ★★★★☆ |

### 9.2 결론

두 프로젝트는 **상호 보완적**:

- **보일러플레이트**: 방법론(GSD) + 코드 분석(RAG) + 에이전트 기억(memory-graph) + 인프라에 강함
- **everything-claude-code**: 자동화(후크) + 서브에이전트 분리 + 토큰 경제학 + 보안 자동 검증에 강함

**가장 효과적인 조합**: 보일러플레이트의 GSD 사이클 위에 everything-claude-code의 후크/서브에이전트/모델 분리를 선택적으로 얹는 구조.

---

## Sources

- `everything-claude-code/README.md`
- `everything-claude-code/the-shortform-guide.md`
- `everything-claude-code/the-longform-guide.md`
- `everything-claude-code/agents/` (12 에이전트 정의)
- `everything-claude-code/skills/` (15+ 스킬)
- `everything-claude-code/commands/` (23+ 명령)
- `everything-claude-code/rules/` (8 규칙 파일)
- `everything-claude-code/hooks/` (hooks.json + 6 스크립트)
- `everything-claude-code/contexts/` (3 동적 프롬프트)
- `everything-claude-code/mcp-configs/mcp-servers.json` (14 MCP)
- `everything-claude-code/scripts/lib/utils.js` (398줄)
- `everything-claude-code/.claude-plugin/plugin.json`
