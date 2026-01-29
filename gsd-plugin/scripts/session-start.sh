#!/bin/bash
# Hook: SessionStart — GSD 상태 자동 로드
# 세션 시작 시 .gsd/STATE.md와 git status를 additionalContext로 주입
set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
STATE_FILE="$PROJECT_DIR/.gsd/STATE.md"
CONTEXT_PARTS=()

# 1. GSD STATE.md 로드 (상위 80줄)
if [ -f "$STATE_FILE" ]; then
    STATE_CONTENT=$(head -80 "$STATE_FILE" 2>/dev/null || true)
    if [ -n "$STATE_CONTENT" ]; then
        CONTEXT_PARTS+=("## GSD State (auto-loaded from .gsd/STATE.md)")
        CONTEXT_PARTS+=("$STATE_CONTENT")
    fi
fi

# 2. Git 미커밋 변경사항 요약
GIT_STATUS=$(git -C "$PROJECT_DIR" status --short 2>/dev/null || true)
if [ -n "$GIT_STATUS" ]; then
    FILE_COUNT=$(echo "$GIT_STATUS" | wc -l | tr -d ' ')
    CONTEXT_PARTS+=("")
    CONTEXT_PARTS+=("## Uncommitted Changes ($FILE_COUNT files)")
    CONTEXT_PARTS+=("$GIT_STATUS")
fi

# 3. 최근 커밋 3개
RECENT_COMMITS=$(git -C "$PROJECT_DIR" log --oneline -3 2>/dev/null || true)
if [ -n "$RECENT_COMMITS" ]; then
    CONTEXT_PARTS+=("")
    CONTEXT_PARTS+=("## Recent Commits")
    CONTEXT_PARTS+=("$RECENT_COMMITS")
fi

# 컨텍스트가 있으면 JSON으로 출력
if [ ${#CONTEXT_PARTS[@]} -gt 0 ]; then
    COMBINED=""
    for part in "${CONTEXT_PARTS[@]}"; do
        COMBINED="${COMBINED}${part}
"
    done
    # Python으로 JSON escape 처리
    python3 -c "
import json, sys
ctx = sys.stdin.read().strip()
if ctx:
    print(json.dumps({
        'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': ctx
        }
    }))
" <<< "$COMBINED"
fi

exit 0
