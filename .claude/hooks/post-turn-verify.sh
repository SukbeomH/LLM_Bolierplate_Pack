#!/usr/bin/env bash
# Hook: Stop — 대화 턴 종료 시 코드 품질 게이트
# Qlty 우선 → ruff fallback (하위 호환)
# 수정된 소스 파일이 있으면 lint 결과를 경고로 출력

main() {
    set -uo pipefail

    PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
    HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"

    # JSON 파싱 추상화 로드
    source "$HOOK_DIR/_json_parse.sh"

    # stdin에서 JSON 읽기
    INPUT=$(cat)

    # stop_hook_active 확인 — 무한 루프 방지
    IS_ACTIVE=$(json_get "$INPUT" '.stop_hook_active // empty')

    if [[ "$IS_ACTIVE" == "True" || "$IS_ACTIVE" == "true" ]]; then
        echo '{"status":"skipped","reason":"stop_hook_active"}'
        exit 0
    fi

    # ─────────────────────────────────────────────────────
    # CRLF → LF 변환 (쉘 스크립트, Python, JSON, YAML)
    # ─────────────────────────────────────────────────────

    CRLF_FIXED=0
    while IFS= read -r line; do
        status="${line:0:2}"
        file="${line:3}"
        if [[ "$status" == *D* ]]; then
            continue
        fi
        filepath="$PROJECT_DIR/$file"
        if [[ -f "$filepath" ]] && [[ "$file" =~ \.(sh|bash|py|json|yaml|yml|md)$ ]]; then
            if file "$filepath" | grep -q "CRLF"; then
                sed -i '' $'s/\r$//' "$filepath"
                CRLF_FIXED=$((CRLF_FIXED + 1))
            fi
        fi
    done < <(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null || true)

    # ─────────────────────────────────────────────────────
    # 변경된 소스 파일 감지 (모든 언어)
    # ─────────────────────────────────────────────────────

    CODE_PATTERN='\.(py|ts|tsx|js|jsx|mjs|cjs|go|rs|java)$'
    CHANGED_FILES=""
    PY_ONLY=true

    while IFS= read -r line; do
        status="${line:0:2}"
        file="${line:3}"
        if [[ "$status" == *D* ]]; then
            continue
        fi
        if [[ "$file" =~ $CODE_PATTERN ]] && [[ -f "$PROJECT_DIR/$file" ]]; then
            CHANGED_FILES="${CHANGED_FILES} ${file}"
            if [[ "$file" != *.py ]]; then
                PY_ONLY=false
            fi
        fi
    done < <(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null || true)

    CHANGED_FILES=$(echo "$CHANGED_FILES" | xargs)

    if [[ -z "$CHANGED_FILES" ]]; then
        echo '{"status":"skipped","reason":"no_code_changes"}'
        exit 0
    fi

    # ─────────────────────────────────────────────────────
    # Qlty 우선 → ruff fallback
    # ─────────────────────────────────────────────────────

    LINT_OUTPUT=""
    ISSUE_COUNT=0

    if command -v qlty &>/dev/null && [[ -f "$PROJECT_DIR/.qlty/qlty.toml" ]]; then
        # Qlty check (변경된 파일 대상)
        LINT_OUTPUT=$(cd "$PROJECT_DIR" && qlty check 2>&1 || true)
        # qlty check 출력에서 이슈 개수 추출
        ISSUE_COUNT=$(echo "$LINT_OUTPUT" | grep -cE '^\s*(error|warning|E[0-9]|W[0-9])' || echo "0")
        # qlty가 에러 개수를 출력하는 경우
        QLTY_ERRORS=$(echo "$LINT_OUTPUT" | grep -oE '[0-9]+ (error|issue|problem)' | grep -oE '[0-9]+' | head -1 || echo "")
        if [[ -n "$QLTY_ERRORS" && "$QLTY_ERRORS" -gt 0 ]]; then
            ISSUE_COUNT="$QLTY_ERRORS"
        fi
    else
        # Fallback: Python 파일만 ruff check
        PY_CHANGES=""
        for f in $CHANGED_FILES; do
            if [[ "$f" == *.py ]]; then
                PY_CHANGES="$PY_CHANGES $f"
            fi
        done
        PY_CHANGES=$(echo "$PY_CHANGES" | xargs)

        if [[ -z "$PY_CHANGES" ]]; then
            echo '{"status":"skipped","reason":"no_python_changes_and_no_qlty"}'
            exit 0
        fi

        LINT_OUTPUT=$(cd "$PROJECT_DIR" && uv run ruff check --no-fix $PY_CHANGES 2>/dev/null || true)

        if [[ -n "$LINT_OUTPUT" ]]; then
            ISSUE_COUNT=$(echo "$LINT_OUTPUT" | grep -oE 'Found [0-9]+ errors?' | grep -oE '[0-9]+' || echo "0")
        fi
    fi

    if [[ "$ISSUE_COUNT" -gt 0 ]]; then
        ISSUES_PREVIEW=$(echo "$LINT_OUTPUT" | head -10)
        ISSUES_JSON=$(json_dumps "$ISSUES_PREVIEW")
        echo "{\"status\":\"warning\",\"lint_issues\":${ISSUE_COUNT},\"preview\":${ISSUES_JSON}}"
        exit 0
    fi

    if [[ "$CRLF_FIXED" -gt 0 ]]; then
        echo "{\"status\":\"success\",\"lint_issues\":0,\"crlf_fixed\":${CRLF_FIXED}}"
    else
        echo '{"status":"success","lint_issues":0}'
    fi
}

# 메인 실행 및 에러 캡처
ERROR_OUTPUT=$(main 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ] || echo "$ERROR_OUTPUT" | grep -qiE '(error|permission denied|no such file)'; then
    HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
    source "$HOOK_DIR/_json_parse.sh"
    ERROR_MSG=$(echo "$ERROR_OUTPUT" | head -3 | tr '\n' ' ' | cut -c1-200)
    ERROR_JSON=$(json_dumps "$ERROR_MSG")
    echo "{\"status\":\"error\",\"message\":${ERROR_JSON}}"
else
    echo "$ERROR_OUTPUT"
fi

exit 0
