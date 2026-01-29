# GSD Plugin Release Guide

> 자동 릴리즈 워크플로우 가이드

## 개요

GSD 플러그인은 **release-please**를 사용하여 자동 릴리즈됩니다.
Conventional Commits를 따르면 버전 관리, CHANGELOG 생성, GitHub Release가 자동으로 처리됩니다.

---

## 릴리즈 플로우

```
1. 플러그인 변경 커밋
   git commit -m "feat(gsd-plugin): 새로운 skill 추가"
                    ↓
2. master에 푸시
   git push origin master
                    ↓
3. release-please가 Release PR 자동 생성
   - Title: "chore(gsd-plugin): release 1.1.0"
   - plugin.json 버전 업데이트
   - CHANGELOG.md 업데이트
                    ↓
4. PR 리뷰 후 머지
                    ↓
5. 자동 릴리즈
   - Git 태그: gsd-plugin-v1.1.0
   - GitHub Release 생성
   - gsd-plugin-1.1.0.zip 첨부
```

---

## Conventional Commits 가이드

### 버전 범프 규칙

| 커밋 타입 | 버전 변경 | 예시 |
|----------|----------|------|
| `fix` | 패치 (1.0.0 → 1.0.1) | 버그 수정, 오타 수정 |
| `feat` | 마이너 (1.0.0 → 1.1.0) | 새 기능, 새 명령어 |
| `feat!` 또는 `BREAKING CHANGE` | 메이저 (1.0.0 → 2.0.0) | 호환성 깨지는 변경 |

### 커밋 메시지 형식

```
<type>(gsd-plugin): <description>

[optional body]

[optional footer]
```

### 예시

```bash
# 버그 수정 → 패치 버전 업
git commit -m "fix(gsd-plugin): hook 스크립트 경로 수정"

# 새 기능 → 마이너 버전 업
git commit -m "feat(gsd-plugin): 새로운 /gsd:analyze 명령 추가"

# 호환성 깨지는 변경 → 메이저 버전 업
git commit -m "feat(gsd-plugin)!: hook API 변경

BREAKING CHANGE: PreToolUse hook의 반환 형식이 변경되었습니다."

# 문서 수정 (CHANGELOG에 포함, 버전 변경 없음)
git commit -m "docs(gsd-plugin): README 설치 가이드 업데이트"

# 리팩토링 (CHANGELOG에 포함, 버전 변경 없음)
git commit -m "refactor(gsd-plugin): skill 스크립트 구조 개선"

# 유지보수 (CHANGELOG에서 숨김)
git commit -m "chore(gsd-plugin): 불필요한 파일 정리"
```

### 지원되는 타입

| 타입 | CHANGELOG 섹션 | 버전 영향 |
|------|---------------|----------|
| `feat` | Features | 마이너 버전 업 |
| `fix` | Bug Fixes | 패치 버전 업 |
| `perf` | Performance | 패치 버전 업 |
| `refactor` | Refactoring | 없음 |
| `docs` | Documentation | 없음 |
| `chore` | (숨김) | 없음 |

---

## 수동 릴리즈

### GitHub Actions에서 수동 트리거

1. GitHub 저장소 → Actions 탭
2. "Release GSD Plugin" 워크플로우 선택
3. "Run workflow" 버튼 클릭
4. master 브랜치 선택 후 실행

### 로컬에서 테스트

```bash
# 현재 버전 확인
cat gsd-plugin/.claude-plugin/plugin.json | jq .version

# 매니페스트 버전 확인
cat .release-please-manifest.json
```

---

## 파일 구조

```
/
├── .github/workflows/
│   └── release-plugin.yml      # 릴리즈 워크플로우
├── release-please-config.json  # release-please 설정
├── .release-please-manifest.json # 버전 추적
└── gsd-plugin/
    ├── .claude-plugin/
    │   └── plugin.json         # 버전 포함 (자동 업데이트)
    ├── CHANGELOG.md            # 변경 이력 (자동 업데이트)
    └── RELEASE.md              # 이 문서
```

---

## 릴리즈 아티팩트

각 릴리즈에는 다음이 포함됩니다:

- **Git 태그**: `gsd-plugin-v{version}` (예: `gsd-plugin-v1.2.0`)
- **GitHub Release**: 자동 생성된 릴리즈 노트
- **ZIP 파일**: `gsd-plugin-{version}.zip`

### ZIP에서 제외되는 파일

```
.git/*
__pycache__/*
*.pyc
.pytest_cache/*
node_modules/*
.env
.venv/*
*.log
.DS_Store
```

---

## 설치 (사용자용)

### GitHub Release에서 설치

```bash
# 최신 릴리즈 다운로드
curl -L https://github.com/SukbeomH/LLM_Bolierplate_Pack/releases/latest/download/gsd-plugin-*.zip -o gsd-plugin.zip

# 플러그인 디렉토리에 압축 해제
unzip gsd-plugin.zip -d ~/.claude/plugins/gsd
```

### 특정 버전 설치

```bash
VERSION="1.2.0"
curl -L "https://github.com/SukbeomH/LLM_Bolierplate_Pack/releases/download/gsd-plugin-v${VERSION}/gsd-plugin-${VERSION}.zip" -o gsd-plugin.zip
unzip gsd-plugin.zip -d ~/.claude/plugins/gsd
```

---

## 문제 해결

### Release PR이 생성되지 않음

1. 커밋 메시지가 Conventional Commits 형식인지 확인
2. `(gsd-plugin)` 스코프가 포함되어 있는지 확인
3. `gsd-plugin/` 디렉토리 내 파일이 변경되었는지 확인

### 버전이 올라가지 않음

- `chore`, `style`, `test` 타입은 버전에 영향을 주지 않음
- `fix` 또는 `feat` 타입을 사용해야 버전이 올라감

### ZIP 파일이 첨부되지 않음

- Release PR이 머지되어야 ZIP 생성 job이 실행됨
- Actions 탭에서 워크플로우 실행 상태 확인

---

## 참고 자료

- [release-please](https://github.com/googleapis/release-please)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Claude Code Plugins](https://code.claude.com/docs/en/plugins)
