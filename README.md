# Developer Boilerplate

AI 에이전트 기반 개발을 위한 경량 프로젝트 보일러플레이트. code-graph-rag(AST 인덱싱) + memory-graph(에이전트 기억)와 GSD(Get Shit Done) 문서 기반 방법론을 결합하여 구조화된 개발 워크플로우를 제공합니다.

## 디렉토리 구조

```
.
├── .agent/            — 에이전트 설정 (symlinks, GSD 워크플로우)
├── .claude/           — Claude Code 스킬 및 설정
├── .gemini/           — Gemini 설정
├── .github/           — GitHub 에이전트 스펙 & 이슈 템플릿
├── .gsd/              — GSD 문서, 템플릿, 예제
├── .specs/            — 명세 템플릿 (실제 문서는 .gsd/에 생성)
├── .vscode/           — VS Code 워크스페이스 설정 & 권장 확장
├── .mcp.json          — MCP 서버 연결 설정 (Claude Code)
├── scripts/           — 유틸리티 스크립트
├── .env.example       — 환경변수 템플릿
├── docker-compose.yml — Memgraph (code-graph-rag 백엔드)
├── Makefile           — 개발 명령어 (make help)
├── pyproject.toml     — Python 프로젝트 설정 (uv)
└── CLAUDE.md          — Claude Code 지침
```

---

## Prerequisites

다음 도구가 시스템에 설치되어 있어야 합니다.

| 도구 | 용도 | 설치 |
|------|------|------|
| **Docker** | Memgraph 컨테이너 | [docker.com](https://docs.docker.com/get-docker/) |
| **uv** | Python 패키지 관리 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **pipx** | CLI 도구 격리 설치 | `brew install pipx && pipx ensurepath` |
| gh CLI | GitHub PR/Issue (선택) | `brew install gh` |

설치 여부 확인:

```bash
make check-deps
```

---

## Quick Start

### 원클릭 셋업

```bash
make setup
```

이 명령은 다음을 순서대로 수행합니다:

1. **code-graph-rag** 클론 + 의존성 설치 → `~/code-graph-rag`
2. **memorygraph** 설치 (pipx)
3. `.env` 파일 생성 (`.env.example` 복사)
4. **Memgraph** Docker 컨테이너 시작
5. 코드베이스 **인덱싱** (Tree-sitter → Memgraph)

셋업 완료 후:

```bash
# 1. .env 파일에서 API 키 설정
#    - CYPHER_API_KEY (Gemini API key — code-graph-rag에서 자연어→Cypher 변환에 사용)
#    - CONTEXT7_API_KEY (선택)

# 2. Claude Code 재시작하여 MCP 서버 로드
```

---

## 수동 설치 (단계별)

### Step 1: 외부 도구 설치

```bash
# code-graph-rag: AST 코드 분석 MCP 서버
make install-code-graph-rag
# 기본 설치 경로: ~/code-graph-rag
# 변경하려면: CODE_GRAPH_RAG_PATH=/your/path make install-code-graph-rag

# memorygraph: 에이전트 영구 기억 MCP 서버
make install-memorygraph
```

### Step 2: 환경 변수 설정

```bash
make init-env       # .env.example → .env 복사
```

`.env` 파일을 열고 다음을 설정합니다:

```bash
# 필수
CYPHER_API_KEY=your-gemini-api-key    # Google AI Studio에서 발급

# code-graph-rag 경로 (기본값: ~/code-graph-rag)
# 다른 경로에 설치했다면 변경
CODE_GRAPH_RAG_PATH=/your/custom/path

# 선택
CONTEXT7_API_KEY=your-key             # Context7 MCP 사용 시
```

### Step 3: 인프라 시작

```bash
make up             # Memgraph Docker 컨테이너 시작
make status         # 상태 확인
```

### Step 4: 코드베이스 인덱싱

```bash
make index          # Tree-sitter 파싱 → Memgraph 그래프 저장
```

### Step 5: MCP 서버 확인

`.mcp.json`이 `CODE_GRAPH_RAG_PATH` 환경변수를 참조합니다.
Claude Code를 재시작하면 자동으로 MCP 서버에 연결됩니다.

```bash
make status         # 전체 상태 확인 (Docker + MCP tools + .env)
```

---

## 설치 경로 커스터마이징

모든 경로는 `.env` 파일 또는 환경변수로 제어됩니다. 하드코딩된 경로는 없습니다.

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `CODE_GRAPH_RAG_PATH` | `~/code-graph-rag` | code-graph-rag 설치 경로 |
| `TARGET_REPO_PATH` | `.` | 분석 대상 저장소 경로 |
| `CYPHER_PROVIDER` | `google` | LLM 프로바이더 |
| `CYPHER_MODEL` | `gemini-2.0-flash` | Cypher 생성 모델 |

팀원에게 공유 시:

```bash
# 1. 저장소 클론
git clone <repo-url> && cd <repo>

# 2. 원클릭 셋업
make setup

# 3. .env에서 API 키 설정
# 4. Claude Code 재시작
```

---

## Make 명령어

```bash
make help                   # 전체 명령어 목록
```

### 설치/설정

| 명령어 | 설명 |
|--------|------|
| `make setup` | 전체 초기 설정 (설치 → 환경 → Memgraph → 인덱싱) |
| `make check-deps` | 필수 도구 설치 여부 확인 |
| `make install-deps` | 모든 외부 의존성 설치 |
| `make install-code-graph-rag` | code-graph-rag 클론 + 설치 |
| `make install-memorygraph` | memorygraph 설치 (pipx) |
| `make init-env` | `.env.example` → `.env` 생성 |

### 인프라

| 명령어 | 설명 |
|--------|------|
| `make up` | Memgraph 시작 |
| `make down` | Memgraph 중지 |
| `make status` | Docker + MCP 도구 + 환경 상태 확인 |
| `make logs` | Memgraph 로그 |
| `make index` | 코드베이스 인덱싱 (code-graph-rag) |
| `make clean` | Docker 볼륨 + 인덱스 삭제 |

### 코드 품질

| 명령어 | 설명 |
|--------|------|
| `make lint` | Ruff 린트 |
| `make lint-fix` | Ruff 자동 수정 |
| `make test` | pytest 실행 |
| `make typecheck` | mypy 타입 체크 |
| `make validate` | SPEC.md 구조 검증 |

---

## GSD 워크플로우

```
/new-project    → SPEC.md 작성
/plan           → 페이즈별 실행 계획 생성
/execute        → 웨이브 단위 구현 (atomic commits)
/verify         → 필수 요구사항 검증
```

전체 29개 워크플로우: `/help` 참조

---

## 핵심 도구

### code-graph-rag (코드 분석)

Tree-sitter + Memgraph 기반 AST 코드 분석. 자연어로 코드베이스를 쿼리합니다.

| MCP Tool | 용도 |
|----------|------|
| `query_code_graph` | 자연어 코드 검색, 의존성/구조/품질 분석 |
| `index_repository` | 코드베이스 인덱싱 |

### memory-graph (에이전트 기억)

에이전트가 세션 간 학습한 패턴, 결정, 컨벤션을 영구 저장합니다.

| MCP Tool | 용도 |
|----------|------|
| `store_memory` | 패턴, 결정, 학습 내용 저장 |
| `recall_memories` | 자연어 기반 기억 검색 |
| `search_memories` | 필터 기반 고급 검색 |
| `create_domain` / `select_domain` | 프로젝트별 메모리 도메인 관리 |

---

## 개발 환경 (IDE)

### VS Code 확장프로그램

프로젝트를 열면 `.vscode/extensions.json`에 정의된 권장 확장을 자동으로 안내합니다.

| 확장프로그램 | ID | 역할 |
|---|---|---|
| Ruff | `charliermarsh.ruff` | 린터 + 포매터 (네이티브 서버) |
| Python | `ms-python.python` | 인터프리터, 디버깅, 환경 관리 |
| Mypy Type Checker | `ms-python.mypy-type-checker` | 타입 체크 (Protocol/ABC 계약 검증) |
| Ruff Ignore Explainer | `jannchie.ruff-ignore-explainer` | `pyproject.toml`의 `select`/`ignore` 규칙 설명 인라인 표시 |

### Ruff 규칙

`pyproject.toml`에 다음 규칙이 활성화되어 있습니다:

| 규칙 | 설명 |
|------|------|
| `E` | pycodestyle errors |
| `F` | pyflakes |
| `I` | isort (import 정렬) |
| `N` | pep8-naming (네이밍 컨벤션) |
| `W` | pycodestyle warnings |
| `B` | flake8-bugbear (ABC 검증, 버그 패턴) |
| `C90` | McCabe complexity (순환 복잡도 ≤ 10) |
| `PL` | Pylint (인자 ≤ 6, 리턴 ≤ 6) |
| `TC` | flake8-type-checking (타입 전용 import 분리) |

---

## 에이전트 설정

| 에이전트 | 설정 파일 |
|----------|-----------|
| **GitHub Agents** | `.github/agents/agent.md` |
| **Claude Code** | `.claude/skills/`, `CLAUDE.md` |
| **Gemini** | `.gemini/GEMINI.md` |

---

## Troubleshooting

### Memgraph 연결 실패

```bash
make up             # 컨테이너 재시작
make logs           # 로그 확인
docker compose ps   # 상태 확인 (ports: 7687, 7444)
```

### code-graph-rag MCP 서버 연결 실패

```bash
# .env에 CODE_GRAPH_RAG_PATH가 올바르게 설정되었는지 확인
make status

# 수동 테스트
cd $CODE_GRAPH_RAG_PATH && uv run graph-code --help
```

### memorygraph 연결 실패

```bash
# 설치 확인
which memorygraph
memorygraph --version

# 재설치
pipx reinstall memorygraphMCP
```

### 인덱싱 실패

```bash
# Memgraph가 실행 중인지 확인
make up && sleep 5 && make index
```

---

## 사용자 정의

이 보일러플레이트를 프로젝트에 맞게 수정하세요:

1. `.env` — `PROJECT_ID`, `CYPHER_API_KEY` 설정
2. `.gsd/SPEC.md` — 프로젝트 요구사항 정의 (`/new-project`로 생성)
3. `.mcp.json` — MCP 서버 연결 설정 (추가 서버 등록 시)
