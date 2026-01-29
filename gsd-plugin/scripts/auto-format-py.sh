#!/bin/bash
# Hook: PostToolUse (Edit|Write) — Python 파일 자동 포맷
# .py 파일 수정 후 ruff format + ruff check --fix 자동 실행
set -uo pipefail

# stdin에서 JSON 읽기
INPUT=$(cat)

# file_path 추출
FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', ''))
except:
    pass
" 2>/dev/null)

# .py 파일이 아니면 종료
if [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" != *.py ]]; then
    exit 0
fi

# 파일이 존재하는지 확인
if [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# ruff format 실행 (자동 포맷)
uv run ruff format "$FILE_PATH" 2>/dev/null || true

# ruff check --fix 실행 (자동 수정 가능한 린트 이슈)
uv run ruff check --fix "$FILE_PATH" 2>/dev/null || true

exit 0
