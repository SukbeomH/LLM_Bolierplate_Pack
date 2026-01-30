# CHANGELOG

> 세션별 코드 및 문서 변경사항 기록
> 자동 생성됨 (SessionEnd 훅)

---

## 변경 기록

<!-- 아래에 세션별 변경사항이 자동으로 추가됩니다 -->

### [2026-01-30] Qlty CLI 통합 및 SC 경험적 검증

**커밋**: `e1a2e3a`, `9345630`, `e4c60d7`, `01e1f7d`

#### 주요 변경
- Qlty CLI 초기화 (`.qlty/qlty.toml`) — ruff, bandit, shellcheck 등 8개 플러그인 자동 감지
- `project-config.yaml` 생성 — python/uv/pytest 설정 통합
- `bootstrap.sh`에 qlty 설치 자동화 추가
- `.mcp.json` FalkorDBLite 백엔드 전환
- `Makefile` qlty 관련 타겟 추가
- Success Criteria 8/9 경험적 검증 완료 (SC#2,4,7,9 추가 검증)

#### 수정된 파일
- `.gsd/SPEC.md` — SC 체크리스트 업데이트
- `.mcp.json` — MCP 서버 설정
- `Makefile` — 빌드 타겟
- `scripts/bootstrap.sh` — 부트스트랩 스크립트

#### 새 파일
- `.qlty/qlty.toml`, `.qlty/.gitignore`, `.qlty/configs/.shellcheckrc`
- `.gsd/project-config.yaml`

---

### [2026-01-30] 훅 자동화 경량화 및 MCP 메모리 저장

**커밋**: `c482d6d`

#### 주요 변경
- `post-turn-index.sh`, `post-turn-verify.sh` 경량화
- `mcp-store-memory.sh`, `stop-context-save.sh` 신규 추가
- `.claude/settings.json` 훅 설정 업데이트

#### 수정된 파일
- `.claude/hooks/post-turn-index.sh`
- `.claude/hooks/post-turn-verify.sh`
- `.claude/settings.json`

#### 새 파일
- `.claude/hooks/mcp-store-memory.sh`
- `.claude/hooks/stop-context-save.sh`

---

### [2026-01-30] 리서치 및 SPEC 작성

**커밋**: `75bceff` 이전

#### 주요 변경
- Multi-Language Support SPEC 작성 (Qlty 통합 설계)
- 4개 리서치 문서 작성: Python 종속성 감사, 다국어 지원, 선행 사례, OpenCode 플러그인

#### 새 파일
- `.gsd/research/RESEARCH-python-specific-audit.md`
- `.gsd/research/RESEARCH-multi-language-support.md`
- `.gsd/research/RESEARCH-prior-art-multi-language.md`
- `.gsd/research/RESEARCH-opencode-plugin-migration.md`

---

### [2026-01-29] 훅 시스템 리팩토링

**커밋**: `7cefb35f`, `8a4d4825`

#### 주요 변경
- 훅 스크립트 6개 전면 리팩토링 (post-turn, pre-compact, save-session, save-transcript, session-start)
- GSD 문서 업데이트 (ARCHITECTURE.md, STACK.md, STATE.md)

#### 수정된 파일
- `.claude/hooks/post-turn-index.sh`
- `.claude/hooks/post-turn-verify.sh`
- `.claude/hooks/pre-compact-save.sh`
- `.claude/hooks/save-session-changes.sh`
- `.claude/hooks/save-transcript.sh`
- `.claude/hooks/session-start.sh`
- `.gsd/ARCHITECTURE.md`
- `.gsd/STACK.md`
- `.gsd/STATE.md`

---
