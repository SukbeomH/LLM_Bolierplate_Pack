# System Prompt Patching Guide

## Purpose

Claude Code CLI의 시스템 프롬프트를 패칭하여 토큰 사용량을 줄인다.
시스템 프롬프트는 모든 대화 턴마다 전송되므로, 불필요한 예시/반복을 제거하면 **컨텍스트 윈도우의 유효 용량이 증가**한다.

- **효과**: 시스템 프롬프트 ~50% 축소 (약 30-40KB → 15-20KB)
- **원리**: CLI 번들(cli.js) 내 프롬프트 텍스트를 regex 기반 find/replace로 압축
- **안전성**: 백업 후 패칭, 언제든 원복 가능
- **범위**: 의미는 보존하고 중복/예시/장황한 설명만 제거

## Prerequisites

- Node.js 18+ (npm 포함)
- Claude Code 설치 (버전 확인: `claude --version`)
- 해당 버전의 패치 파일 (`claude-code-tips/system-prompt/<version>/`)

## Quick Start (Local npm)

네이티브 바이너리 추출 없이, **로컬 npm 설치**로 패칭하는 방법.

```bash
# 1. 현재 Claude Code 버전 확인
claude --version   # e.g., 2.1.21

# 2. Makefile 타겟으로 패칭 (권장)
make patch-prompt

# 3. 패칭된 버전 실행
DISABLE_AUTOUPDATER=1 npx --prefix .patch-workspace claude
```

## Manual Steps

Makefile 없이 수동으로 진행하는 경우:

```bash
VERSION=$(claude --version | awk '{print $1}')
PATCH_DIR=claude-code-tips/system-prompt/${VERSION}

# 1. 로컬 설치
mkdir -p .patch-workspace
npm install --prefix .patch-workspace @anthropic-ai/claude-code@${VERSION}

# 2. 백업 생성
CLI_JS=.patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js
cp "${CLI_JS}" "${CLI_JS}.backup"

# 3. 패치 적용 (node_modules 경로 우회를 위해 임시 복사)
cp "${CLI_JS}" /tmp/_claude_cli.js
cp "${CLI_JS}.backup" /tmp/_claude_cli.js.backup
node "${PATCH_DIR}/patch-cli.js" /tmp/_claude_cli.js
cp /tmp/_claude_cli.js "${CLI_JS}"

# 4. 실행
DISABLE_AUTOUPDATER=1 npx --prefix .patch-workspace claude
```

## DISABLE_AUTOUPDATER

Claude Code는 기본적으로 자동 업데이트를 수행한다. 패칭된 cli.js가 업데이트로 덮어씌워지는 것을 방지하려면:

```bash
# .env 또는 셸 환경에 설정
export DISABLE_AUTOUPDATER=1
```

direnv 사용 시 `.env`에 추가하면 프로젝트 디렉토리 진입 시 자동 적용된다.

## Version Upgrade

새 버전의 Claude Code가 출시되면 패치를 업데이트해야 한다:

1. 새 버전 디렉토리 생성: `cp -r system-prompt/OLD system-prompt/NEW`
2. `patch-cli.js`의 `EXPECTED_VERSION`과 `EXPECTED_HASHES` 업데이트
3. 실패하는 패치 수정 (divergence point 찾기 → find.txt/replace.txt 업데이트)
4. 상세 가이드: `claude-code-tips/system-prompt/UPGRADING.md`

## Cross-Platform Notes

| Platform | Install Method | Patch Target |
|----------|---------------|--------------|
| macOS / Linux | `npm install` (local) | `node_modules/@anthropic-ai/claude-code/cli.js` |
| Windows | `npm install` (local) | 동일 경로 |
| Docker | `npm install -g` (container 내) | `/usr/local/lib/node_modules/@anthropic-ai/claude-code/cli.js` |

네이티브 바이너리 설치(`curl -fsSL https://claude.ai/install.sh | bash`)를 사용하는 경우,
`node-lief`를 통한 추출/리팩 과정이 필요하다. 상세: `claude-code-tips/system-prompt/UPGRADING.md` > Native Binary Patching.

## Restore

```bash
# npm 설치 방식
cp .patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js.backup \
   .patch-workspace/node_modules/@anthropic-ai/claude-code/cli.js

# 또는 재설치
rm -rf .patch-workspace
```

## Verification

```bash
# 기본 동작 확인
DISABLE_AUTOUPDATER=1 npx --prefix .patch-workspace claude --version

# 프롬프트 손상 확인
DISABLE_AUTOUPDATER=1 npx --prefix .patch-workspace claude -p \
  'Any [object Object] or broken content in your prompt? Yes or no only.'

# 도구 동작 확인
DISABLE_AUTOUPDATER=1 npx --prefix .patch-workspace claude -p \
  'Run: echo "tools work"' --allowedTools Bash
```

## Reference

- Patch source: [claude-code-tips/system-prompt/](https://github.com/anthropics/claude-code-tips) (external reference)
- Upgrade guide: `claude-code-tips/system-prompt/UPGRADING.md`
- Architecture: `.gsd/ARCHITECTURE.md`
