#!/usr/bin/env bash
# E2E Test: mcp-store-memory.sh 락 메커니즘 + worktree 호환성 검증
# Usage: bash tests/e2e/test_memory_lock.sh

set -uo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
STORE_SCRIPT="$PROJECT_DIR/.claude/hooks/mcp-store-memory.sh"
DB_DIR="$(dirname "$(python3 -c "
import json
with open('$PROJECT_DIR/.mcp.json') as f:
    cfg = json.load(f)
print(cfg['mcpServers']['memory']['env']['MCP_MEMORY_SQLITE_PATH'])
")")"
LOCK_FILE="$DB_DIR/.memory.lock"
LOG="$PROJECT_DIR/tests/e2e/.test_memory_lock.log"

PASS=0
FAIL=0
TOTAL=0

# ─────────────────────────────────────────────────────
# 테스트 헬퍼
# ─────────────────────────────────────────────────────
log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
assert_ok()   { TOTAL=$((TOTAL+1)); if [ "$1" -eq 0 ]; then PASS=$((PASS+1)); log "  PASS: $2"; else FAIL=$((FAIL+1)); log "  FAIL: $2 (exit=$1)"; fi; }
assert_fail() { TOTAL=$((TOTAL+1)); if [ "$1" -ne 0 ]; then PASS=$((PASS+1)); log "  PASS: $2"; else FAIL=$((FAIL+1)); log "  FAIL: $2 (expected failure, got exit=0)"; fi; }
assert_eq()   { TOTAL=$((TOTAL+1)); if [ "$1" = "$2" ]; then PASS=$((PASS+1)); log "  PASS: $3"; else FAIL=$((FAIL+1)); log "  FAIL: $3 (expected='$2', got='$1')"; fi; }

# ─────────────────────────────────────────────────────
# 사전 정리
# ─────────────────────────────────────────────────────
rm -f "$LOCK_FILE" "$LOG"
mkdir -p "$(dirname "$LOG")"
log "=== Memory Lock E2E Test Start ==="
log "PROJECT_DIR: $PROJECT_DIR"
log "DB_DIR: $DB_DIR"
log "LOCK_FILE: $LOCK_FILE"
log ""

# ═════════════════════════════════════════════════════
# Test 1: 단일 store 정상 동작
# ═════════════════════════════════════════════════════
log "── Test 1: Single store ──"
CLAUDE_PROJECT_DIR="$PROJECT_DIR" bash "$STORE_SCRIPT" \
    "E2E Test $(date +%s)" \
    "Single store test content" \
    "e2e-test,auto"
assert_ok $? "단일 store 성공"

# 락 파일 정리 확인
assert_eq "$([ -f "$LOCK_FILE" ] && echo "exists" || echo "clean")" "clean" "락 파일 정리됨"
log ""

# ═════════════════════════════════════════════════════
# Test 2: 동시 실행 — 두 프로세스가 동일 DB에 store
# ═════════════════════════════════════════════════════
log "── Test 2: Concurrent store (2 processes) ──"
TS=$(date +%s)

# 프로세스 A (백그라운드)
CLAUDE_PROJECT_DIR="$PROJECT_DIR" bash "$STORE_SCRIPT" \
    "E2E Concurrent A [$TS]" \
    "Process A content — concurrent test" \
    "e2e-test,concurrent,process-a" &
PID_A=$!

# 프로세스 B (약간의 딜레이 후)
sleep 0.2
CLAUDE_PROJECT_DIR="$PROJECT_DIR" bash "$STORE_SCRIPT" \
    "E2E Concurrent B [$TS]" \
    "Process B content — concurrent test" \
    "e2e-test,concurrent,process-b" &
PID_B=$!

# 두 프로세스 완료 대기
wait $PID_A 2>/dev/null; EXIT_A=$?
wait $PID_B 2>/dev/null; EXIT_B=$?

log "  Process A exit=$EXIT_A, Process B exit=$EXIT_B"
# 최소 하나는 성공해야 함
if [ "$EXIT_A" -eq 0 ] || [ "$EXIT_B" -eq 0 ]; then
    assert_ok 0 "동시 실행: 최소 1개 성공"
else
    assert_ok 1 "동시 실행: 최소 1개 성공"
fi

# 둘 다 성공이면 bonus
if [ "$EXIT_A" -eq 0 ] && [ "$EXIT_B" -eq 0 ]; then
    log "  BONUS: 두 프로세스 모두 성공 (락 대기 동작 확인)"
fi

# 락 파일 정리 확인
sleep 1
assert_eq "$([ -f "$LOCK_FILE" ] && echo "exists" || echo "clean")" "clean" "동시 실행 후 락 파일 정리됨"
log ""

# ═════════════════════════════════════════════════════
# Test 3: stale lock 자동 제거
# ═════════════════════════════════════════════════════
log "── Test 3: Stale lock recovery ──"
mkdir -p "$DB_DIR"
echo "99999" > "$LOCK_FILE"
# 파일 mtime을 2분 전으로 변경 (60초 임계값 초과)
touch -t "$(date -v-2M '+%Y%m%d%H%M.%S')" "$LOCK_FILE"

CLAUDE_PROJECT_DIR="$PROJECT_DIR" bash "$STORE_SCRIPT" \
    "E2E Stale Lock Recovery $(date +%s)" \
    "Should succeed after stale lock removal" \
    "e2e-test,stale-lock"
assert_ok $? "stale lock 자동 제거 후 store 성공"
assert_eq "$([ -f "$LOCK_FILE" ] && echo "exists" || echo "clean")" "clean" "stale lock 정리 후 락 파일 없음"
log ""

# ═════════════════════════════════════════════════════
# Test 4: lock timeout — 활성 락이 있을 때 10초 후 skip
# ═════════════════════════════════════════════════════
log "── Test 4: Lock timeout (active lock, expect skip) ──"
mkdir -p "$DB_DIR"
echo "99999" > "$LOCK_FILE"
# mtime을 현재로 (stale이 아닌 활성 락)
touch "$LOCK_FILE"

# 타임아웃 테스트 (10초 대기 후 실패 예상) — 빠르게 하기 위해 서브셸에서 retries를 오버라이드할 수 없으므로 실제 대기
# 대신 짧은 timeout으로 감싸서 검증
START_T=$(date +%s)
timeout 15 bash -c "CLAUDE_PROJECT_DIR='$PROJECT_DIR' bash '$STORE_SCRIPT' 'E2E Timeout Test' 'Should timeout' 'e2e-test,timeout'" 2>/dev/null
EXIT_TIMEOUT=$?
END_T=$(date +%s)
ELAPSED=$((END_T - START_T))

assert_fail "$([[ $EXIT_TIMEOUT -ne 0 ]] && echo 1 || echo 0)" "활성 락 존재 시 skip (exit≠0)"
log "  대기 시간: ${ELAPSED}초 (10초 근처 예상)"
if [[ "$ELAPSED" -ge 8 && "$ELAPSED" -le 15 ]]; then
    assert_ok 0 "타임아웃 대기 시간 정상 (${ELAPSED}s)"
else
    assert_ok 1 "타임아웃 대기 시간 비정상 (${ELAPSED}s, expected 8-15s)"
fi

# 정리
rm -f "$LOCK_FILE"
log ""

# ═════════════════════════════════════════════════════
# Test 5: pre-compact-save.sh 동기 실행 확인
# ═════════════════════════════════════════════════════
log "── Test 5: pre-compact-save.sh runs synchronously ──"
COMPACT_SCRIPT="$PROJECT_DIR/.claude/hooks/pre-compact-save.sh"
if [ -f "$COMPACT_SCRIPT" ]; then
    # mcp-store-memory.sh 호출 줄에서 & (백그라운드)로 끝나는 줄이 없는지 확인
    BG_SPAWN=$(grep 'mcp-store-memory\.sh' "$COMPACT_SCRIPT" | grep -c ' &$' 2>/dev/null || true)
    assert_eq "${BG_SPAWN:-0}" "0" "pre-compact-save.sh에 백그라운드 spawn 없음"
else
    log "  SKIP: pre-compact-save.sh not found"
fi
log ""

# ═════════════════════════════════════════════════════
# Test 6: .mcp.json pragma 설정 확인
# ═════════════════════════════════════════════════════
log "── Test 6: .mcp.json pragma configuration ──"
PRAGMAS=$(python3 -c "
import json
with open('$PROJECT_DIR/.mcp.json') as f:
    cfg = json.load(f)
env = cfg['mcpServers']['memory']['env']
print(env.get('MCP_MEMORY_SQLITE_PRAGMAS',''))
")
if echo "$PRAGMAS" | grep -q "busy_timeout=15000"; then
    assert_ok 0 "busy_timeout=15000 설정됨"
else
    assert_ok 1 "busy_timeout=15000 설정됨"
fi
if echo "$PRAGMAS" | grep -q "cache_size=20000"; then
    assert_ok 0 "cache_size=20000 설정됨"
else
    assert_ok 1 "cache_size=20000 설정됨"
fi
log ""

# ═════════════════════════════════════════════════════
# Test 7: worktree에서 .mcp.json 탐색 + 락 경로 일치
# ═════════════════════════════════════════════════════
log "── Test 7: Git worktree lock path resolution ──"
WORKTREE_DIR=""
CLEANUP_WORKTREE=""

# 임시 worktree 생성
WORKTREE_DIR="/tmp/boilerplate-worktree-test-$$"
git -C "$PROJECT_DIR" worktree add "$WORKTREE_DIR" HEAD --detach 2>/dev/null
WT_EXIT=$?

if [ "$WT_EXIT" -eq 0 ] && [ -d "$WORKTREE_DIR" ]; then
    CLEANUP_WORKTREE="$WORKTREE_DIR"
    log "  Worktree 생성: $WORKTREE_DIR"

    # worktree는 전체 트리를 체크아웃하므로 tracked 파일인 .mcp.json이 존재할 수 있음
    # 핵심 검증: worktree에서도 동일한 DB 경로의 락 파일을 사용하는지
    log "  worktree .mcp.json 존재: $([ -f "$WORKTREE_DIR/.mcp.json" ] && echo "yes" || echo "no")"

    # worktree에서 store 스크립트가 main의 .mcp.json을 찾는지 확인
    # git rev-parse --git-common-dir 결과 확인
    COMMON=$(git -C "$WORKTREE_DIR" rev-parse --git-common-dir 2>/dev/null)
    MAIN_FROM_COMMON="$(dirname "$COMMON")"
    log "  git-common-dir → main worktree: $MAIN_FROM_COMMON"

    if [ -f "$MAIN_FROM_COMMON/.mcp.json" ]; then
        assert_ok 0 "worktree에서 main의 .mcp.json 탐색 가능"
    else
        assert_ok 1 "worktree에서 main의 .mcp.json 탐색 가능"
    fi

    # worktree에서 실제 store 실행
    CLAUDE_PROJECT_DIR="$WORKTREE_DIR" bash "$STORE_SCRIPT" \
        "E2E Worktree Test $(date +%s)" \
        "Store from worktree path" \
        "e2e-test,worktree"
    assert_ok $? "worktree에서 store 성공"

    # 락 파일이 DB 디렉토리에 생겼다 사라졌는지 확인 (worktree 안이 아님)
    assert_eq "$([ -f "$LOCK_FILE" ] && echo "exists" || echo "clean")" "clean" \
        "worktree store 후 DB 디렉토리 락 정리됨"

    # worktree와 main에서 동시 실행
    log "  동시 실행: main + worktree"
    CLAUDE_PROJECT_DIR="$PROJECT_DIR" bash "$STORE_SCRIPT" \
        "E2E Cross-WT Main $(date +%s)" \
        "Main worktree concurrent" \
        "e2e-test,cross-worktree,main" &
    PID_MAIN=$!

    sleep 0.2
    CLAUDE_PROJECT_DIR="$WORKTREE_DIR" bash "$STORE_SCRIPT" \
        "E2E Cross-WT Secondary $(date +%s)" \
        "Secondary worktree concurrent" \
        "e2e-test,cross-worktree,secondary" &
    PID_WT=$!

    wait $PID_MAIN 2>/dev/null; EXIT_MAIN=$?
    wait $PID_WT 2>/dev/null; EXIT_WT=$?

    log "  Main exit=$EXIT_MAIN, Worktree exit=$EXIT_WT"
    if [ "$EXIT_MAIN" -eq 0 ] || [ "$EXIT_WT" -eq 0 ]; then
        assert_ok 0 "cross-worktree 동시 실행: 최소 1개 성공"
    else
        assert_ok 1 "cross-worktree 동시 실행: 최소 1개 성공"
    fi
    if [ "$EXIT_MAIN" -eq 0 ] && [ "$EXIT_WT" -eq 0 ]; then
        log "  BONUS: main + worktree 모두 성공"
    fi
else
    log "  SKIP: worktree 생성 실패"
fi

# worktree 정리
if [ -n "$CLEANUP_WORKTREE" ] && [ -d "$CLEANUP_WORKTREE" ]; then
    git -C "$PROJECT_DIR" worktree remove "$CLEANUP_WORKTREE" --force 2>/dev/null || true
    log "  Worktree 정리 완료"
fi
log ""

# ═════════════════════════════════════════════════════
# 결과 요약
# ═════════════════════════════════════════════════════
log "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="

# 최종 정리
rm -f "$LOCK_FILE"

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
exit 0
