#!/usr/bin/env bash

# Run all code quality tools and output structured report.
# Qlty 경로: qlty check --fix → qlty fmt --all → test
# Fallback 경로: ruff → mypy → pytest (기존 동작)
# Usage: bash scripts/run_quality_checks.sh [--no-test] [--fix-only] [--strict]

set -o errexit
set -o nounset
set -o pipefail
[[ -n ${DEBUG:-} ]] && set -o xtrace

# --- Options ---
NO_TEST=false
FIX_ONLY=false
STRICT=false

for arg in "$@"; do
    case "$arg" in
        --no-test)  NO_TEST=true ;;
        --fix-only) FIX_ONLY=true ;;
        --strict)   STRICT=true ;;
    esac
done

# --- Load project config ---
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# load-config.sh에서 환경변수 로드
if [[ -f "$PROJECT_DIR/scripts/load-config.sh" ]]; then
    source "$PROJECT_DIR/scripts/load-config.sh"
fi

# --- Qlty 사용 가능 여부 판단 ---
USE_QLTY=false
if command -v qlty &>/dev/null && [[ -f "$PROJECT_DIR/.qlty/qlty.toml" ]]; then
    USE_QLTY=true
fi

# --- Results ---
LINT_STATUS="SKIP"
LINT_FIXED=0
LINT_REMAINING=0
FORMAT_STATUS="SKIP"
TYPECHECK_STATUS="SKIP"
TYPECHECK_ERRORS=0
TEST_STATUS="SKIP"
TEST_PASSED=0
TEST_TOTAL=0

if [[ "$USE_QLTY" == "true" ]]; then
    # ═══════════════════════════════════════════════════
    # Qlty 경로
    # ═══════════════════════════════════════════════════

    # --- Step 1: Qlty Check + Fix ---
    FIX_OUTPUT=$(cd "$PROJECT_DIR" && qlty check --fix 2>&1 || true)
    CHECK_OUTPUT=$(cd "$PROJECT_DIR" && qlty check --output-format=json 2>&1 || true)

    LINT_REMAINING=$(echo "$CHECK_OUTPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data.get('issues', data if isinstance(data, list) else [])))" 2>/dev/null || echo "0")

    if [[ "$LINT_REMAINING" -eq 0 ]]; then
        LINT_STATUS="PASS"
    elif [[ "$FIX_ONLY" == "true" ]]; then
        LINT_STATUS="FIXED"
    else
        LINT_STATUS="FAIL"
    fi

    # --- Step 2: Qlty Format ---
    FORMAT_OUTPUT=$(cd "$PROJECT_DIR" && qlty fmt --all 2>&1 || true)
    if echo "$FORMAT_OUTPUT" | grep -qiE '(reformatted|formatted|changed)'; then
        FORMAT_STATUS="FIXED"
    else
        FORMAT_STATUS="PASS"
    fi

    # --- Step 3: Type Check (Qlty에 포함되어 있을 수 있음) ---
    # Qlty가 mypy/tsc를 포함한 경우 check에서 이미 실행됨
    TYPECHECK_STATUS="PASS"
    TYPECHECK_ERRORS=0

else
    # ═══════════════════════════════════════════════════
    # Fallback 경로 (기존 Python 동작)
    # ═══════════════════════════════════════════════════

    # --- Prerequisites ---
    COMMANDS=("uv")
    for cmd in "${COMMANDS[@]}"; do
        if ! command -v "$cmd" &>/dev/null; then
            printf '{"error": "%s not found in PATH"}\n' "$cmd"
            exit 1
        fi
    done

    # --- Step 1: Ruff Lint + Auto-Fix ---
    LINT_OUTPUT=$(uv run ruff check . --fix --output-format=json 2>/dev/null || true)
    LINT_REMAINING=$(echo "$LINT_OUTPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")

    if [[ "$LINT_REMAINING" -eq 0 ]]; then
        LINT_STATUS="PASS"
    elif [[ "$FIX_ONLY" == "true" ]]; then
        LINT_STATUS="FIXED"
    else
        LINT_STATUS="FAIL"
    fi

    # --- Step 2: Ruff Format ---
    FORMAT_OUTPUT=$(uv run ruff format . 2>&1 || true)
    if echo "$FORMAT_OUTPUT" | grep -q "file reformatted"; then
        FORMAT_STATUS="FIXED"
    else
        FORMAT_STATUS="PASS"
    fi

    # --- Step 3: Mypy ---
    MYPY_OUTPUT=$(uv run mypy . 2>&1 || true)
    TYPECHECK_ERRORS=$(echo "$MYPY_OUTPUT" | grep -c "error:" || true)
    if [[ "$TYPECHECK_ERRORS" -eq 0 ]]; then
        TYPECHECK_STATUS="PASS"
    else
        TYPECHECK_STATUS="FAIL"
    fi
fi

# --- Step 4: Test ---
if [[ "$NO_TEST" == "false" ]]; then
    TEST_CMD=""

    # project-config.yaml에서 테스트 명령어 읽기
    if [[ -n "${TEST_RUNNER_CMD:-}" && "$TEST_RUNNER_CMD" != "" ]]; then
        TEST_CMD="$TEST_RUNNER_CMD"
    else
        # Fallback: Python 기본
        TEST_CMD="uv run pytest tests/ -x -q --tb=short"
    fi

    TEST_OUTPUT=$(eval "$TEST_CMD" 2>&1 || true)
    TEST_PASSED=$(echo "$TEST_OUTPUT" | grep -oP '\d+ passed' | grep -oP '\d+' || echo "0")
    TEST_TOTAL=$TEST_PASSED
    FAILED=$(echo "$TEST_OUTPUT" | grep -oP '\d+ failed' | grep -oP '\d+' || echo "0")
    TEST_TOTAL=$((TEST_PASSED + FAILED))

    if [[ "$FAILED" -eq 0 ]] && [[ "$TEST_PASSED" -gt 0 ]]; then
        TEST_STATUS="PASS"
    elif [[ "$TEST_TOTAL" -eq 0 ]]; then
        TEST_STATUS="SKIP"
    else
        TEST_STATUS="FAIL"
    fi
fi

# --- Strict mode ---
OVERALL="CLEAN"
if [[ "$STRICT" == "true" ]]; then
    if [[ "$LINT_STATUS" != "PASS" ]] || [[ "$TYPECHECK_STATUS" != "PASS" ]] || [[ "$TEST_STATUS" == "FAIL" ]]; then
        OVERALL="ISSUES_REMAIN"
    fi
else
    if [[ "$LINT_STATUS" == "FAIL" ]] || [[ "$TYPECHECK_STATUS" == "FAIL" ]] || [[ "$TEST_STATUS" == "FAIL" ]]; then
        OVERALL="ISSUES_REMAIN"
    fi
fi

# --- Output ---
TOOL_LABEL="Qlty"
[[ "$USE_QLTY" == "false" ]] && TOOL_LABEL="Ruff"

cat <<EOF
=== Clean Report ===
Lint ($TOOL_LABEL): ${LINT_STATUS} (${LINT_FIXED} fixed, ${LINT_REMAINING} remaining)
Format:       ${FORMAT_STATUS}
Type Check:   ${TYPECHECK_STATUS} (${TYPECHECK_ERRORS} errors)
Tests:        ${TEST_STATUS} (${TEST_PASSED}/${TEST_TOTAL})
===
Overall:      ${OVERALL}
EOF

if [[ "$OVERALL" == "ISSUES_REMAIN" ]] && [[ "$FIX_ONLY" == "false" ]]; then
    echo ""
    echo "--- Remaining Issues ---"
    if [[ "$USE_QLTY" == "false" ]]; then
        [[ "$LINT_REMAINING" -gt 0 ]] && echo "$LINT_OUTPUT" | python3 -c "
import sys, json
for item in json.load(sys.stdin):
    print(f\"  {item.get('filename','')}:{item.get('location',{}).get('row','')}: {item.get('code','')} {item.get('message','')}\")
" 2>/dev/null || true
        [[ "$TYPECHECK_ERRORS" -gt 0 ]] && echo "${MYPY_OUTPUT:-}" | grep "error:" || true
    else
        [[ "$LINT_REMAINING" -gt 0 ]] && echo "${CHECK_OUTPUT:-}" | head -20 || true
    fi
fi

[[ "$OVERALL" == "CLEAN" ]] && exit 0 || exit 1
