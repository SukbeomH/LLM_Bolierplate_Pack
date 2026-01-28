#!/usr/bin/env bash

# Run all code quality tools (ruff lint, ruff format, mypy, pytest) and output structured report.
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

# --- Prerequisites ---
COMMANDS=("uv")
for cmd in "${COMMANDS[@]}"; do
    if ! command -v "$cmd" &>/dev/null; then
        printf '{"error": "%s not found in PATH"}\n' "$cmd"
        exit 1
    fi
done

# --- Results ---
RUFF_LINT_STATUS="SKIP"
RUFF_LINT_FIXED=0
RUFF_LINT_REMAINING=0
RUFF_FORMAT_STATUS="SKIP"
MYPY_STATUS="SKIP"
MYPY_ERRORS=0
TEST_STATUS="SKIP"
TEST_PASSED=0
TEST_TOTAL=0

# --- Step 1: Ruff Lint + Auto-Fix ---
LINT_OUTPUT=$(uv run ruff check . --fix --output-format=json 2>/dev/null || true)
RUFF_LINT_REMAINING=$(echo "$LINT_OUTPUT" | python3 -c "import sys,json; data=json.load(sys.stdin); print(len(data))" 2>/dev/null || echo "0")

FIX_OUTPUT=$(uv run ruff check . --diff 2>/dev/null || true)
if [[ "$RUFF_LINT_REMAINING" -eq 0 ]]; then
    RUFF_LINT_STATUS="PASS"
elif [[ "$FIX_ONLY" == "true" ]]; then
    RUFF_LINT_STATUS="FIXED"
else
    RUFF_LINT_STATUS="FAIL"
fi

# --- Step 2: Ruff Format ---
FORMAT_OUTPUT=$(uv run ruff format . 2>&1 || true)
if echo "$FORMAT_OUTPUT" | grep -q "file reformatted"; then
    RUFF_FORMAT_STATUS="FIXED"
else
    RUFF_FORMAT_STATUS="PASS"
fi

# --- Step 3: Mypy ---
MYPY_OUTPUT=$(uv run mypy . 2>&1 || true)
MYPY_ERRORS=$(echo "$MYPY_OUTPUT" | grep -c "error:" || true)
if [[ "$MYPY_ERRORS" -eq 0 ]]; then
    MYPY_STATUS="PASS"
else
    MYPY_STATUS="FAIL"
fi

# --- Step 4: Pytest ---
if [[ "$NO_TEST" == "false" ]]; then
    TEST_OUTPUT=$(uv run pytest tests/ -x -q --tb=short 2>&1 || true)
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
    MYPY_WARNINGS=$(echo "$MYPY_OUTPUT" | grep -c "warning:" || true)
    if [[ "$MYPY_WARNINGS" -gt 0 ]] || [[ "$RUFF_LINT_STATUS" != "PASS" ]] || [[ "$MYPY_STATUS" != "PASS" ]] || [[ "$TEST_STATUS" == "FAIL" ]]; then
        OVERALL="ISSUES_REMAIN"
    fi
else
    if [[ "$RUFF_LINT_STATUS" == "FAIL" ]] || [[ "$MYPY_STATUS" == "FAIL" ]] || [[ "$TEST_STATUS" == "FAIL" ]]; then
        OVERALL="ISSUES_REMAIN"
    fi
fi

# --- Output ---
cat <<EOF
=== Clean Report ===
Ruff Lint:    ${RUFF_LINT_STATUS} (${RUFF_LINT_FIXED} fixed, ${RUFF_LINT_REMAINING} remaining)
Ruff Format:  ${RUFF_FORMAT_STATUS}
Mypy:         ${MYPY_STATUS} (${MYPY_ERRORS} errors)
Tests:        ${TEST_STATUS} (${TEST_PASSED}/${TEST_TOTAL})
===
Overall:      ${OVERALL}
EOF

if [[ "$OVERALL" == "ISSUES_REMAIN" ]] && [[ "$FIX_ONLY" == "false" ]]; then
    echo ""
    echo "--- Remaining Issues ---"
    [[ "$RUFF_LINT_REMAINING" -gt 0 ]] && echo "$LINT_OUTPUT" | python3 -c "
import sys, json
for item in json.load(sys.stdin):
    print(f\"  {item.get('filename','')}:{item.get('location',{}).get('row','')}: {item.get('code','')} {item.get('message','')}\")
" 2>/dev/null || true
    [[ "$MYPY_ERRORS" -gt 0 ]] && echo "$MYPY_OUTPUT" | grep "error:" || true
fi

[[ "$OVERALL" == "CLEAN" ]] && exit 0 || exit 1
