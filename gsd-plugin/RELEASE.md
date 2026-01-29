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

### GitHub Actions PR 생성 권한 오류

**증상:**
```
GitHub Actions is not permitted to create or approve pull requests
```

**해결:**
1. GitHub 저장소 → Settings → Actions → General
2. "Workflow permissions" 섹션에서:
   - ✅ "Read and write permissions" 선택
   - ✅ "Allow GitHub Actions to create and approve pull requests" 체크

### release-please 컴포넌트 출력 변수 문제

**증상:** `build-and-upload` job이 `skipped`로 표시됨

**원인:** release-please v4 모노레포 설정에서 출력 변수명이 컴포넌트 prefix를 포함함

**해결:** 워크플로우에서 출력 변수명 수정
```yaml
# 잘못된 예
release_created: ${{ steps.release.outputs.release_created }}

# 올바른 예 (컴포넌트 prefix 포함)
release_created: ${{ steps.release.outputs['gsd-plugin--release_created'] }}
tag_name: ${{ steps.release.outputs['gsd-plugin--tag_name'] }}
version: ${{ steps.release.outputs['gsd-plugin--version'] }}
```

### 수동 ZIP 업로드 (긴급 시)

릴리즈는 생성되었으나 ZIP이 누락된 경우:

```bash
# 로컬에서 ZIP 생성
cd /path/to/repo
zip -r gsd-plugin-X.Y.Z.zip gsd-plugin/ \
  -x "gsd-plugin/.git/*" \
  -x "gsd-plugin/__pycache__/*" \
  -x "gsd-plugin/*.pyc"

# 기존 릴리즈에 업로드
gh release upload gsd-plugin-vX.Y.Z gsd-plugin-X.Y.Z.zip

# 정리
rm gsd-plugin-X.Y.Z.zip
```

---

## 첫 릴리즈 경험 (v1.1.0)

### 타임라인

| 시간 | 이벤트 |
|------|--------|
| 11:49 | 워크플로우 파일 생성 및 푸시 |
| 11:54 | 워크플로우 실행 → PR 생성 권한 오류 |
| 11:57 | GitHub 설정 변경 후 재실행 |
| 11:57 | Release PR #1 생성 성공 |
| 12:02 | PR 머지 → 릴리즈 생성 |
| 12:02 | ZIP 미첨부 발견 (출력 변수 문제) |
| 12:04 | 수동 ZIP 업로드 |
| 12:05 | 워크플로우 수정 커밋 |

### 발견된 이슈 및 해결

1. **GitHub Actions 권한**
   - 기본 설정에서는 PR 생성 불가
   - 저장소 설정에서 명시적 허용 필요

2. **release-please v4 출력 변수**
   - 모노레포/컴포넌트 설정 시 `component--output` 형식
   - 공식 문서에서 명확히 설명되지 않음

3. **워크플로우 디버깅**
   - `gh run view <id> --log-failed` 로 실패 원인 확인
   - `gh run view <id> --json jobs` 로 job 상태 확인

### 교훈

- 첫 릴리즈 전 테스트 실행 권장 (`workflow_dispatch`)
- 저장소 권한 설정 사전 확인 필수
- release-please 출력 변수는 설정 방식에 따라 다름

---

## 참고 자료

- [release-please](https://github.com/googleapis/release-please)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Claude Code Plugins](https://code.claude.com/docs/en/plugins)
