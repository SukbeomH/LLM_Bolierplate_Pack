#!/usr/bin/env bash
# MCP JSON-RPC를 통해 mcp-memory-service에 메모리 저장
# Usage: mcp-store-memory.sh <title> <content> [tags]
# 동시 접근 방지를 위해 .memory.lock 사용 (post-turn-index.sh 패턴 차용)
# git worktree 호환: 락 파일을 DB 파일 옆에 배치하여 모든 worktree가 동일 락 공유

set -uo pipefail

TITLE="${1:?Usage: mcp-store-memory.sh <title> <content> [tags]}"
CONTENT="${2:?Missing content}"
TAGS="${3:-session-learnings,auto}"

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# ─────────────────────────────────────────────────────
# .mcp.json에서 설정 추출 (락 경로 결정을 위해 먼저 실행)
# ─────────────────────────────────────────────────────

# git worktree 지원: main worktree의 .mcp.json을 우선 탐색
MCP_JSON=""
if [ -f "$PROJECT_DIR/.mcp.json" ]; then
    MCP_JSON="$PROJECT_DIR/.mcp.json"
else
    # worktree인 경우 git commondir로 main worktree 탐색
    COMMON_DIR=$(git -C "$PROJECT_DIR" rev-parse --git-common-dir 2>/dev/null || true)
    if [ -n "$COMMON_DIR" ] && [ -f "$(dirname "$COMMON_DIR")/.mcp.json" ]; then
        MCP_JSON="$(dirname "$COMMON_DIR")/.mcp.json"
    fi
fi

if [ -z "${MCP_MEMORY_SQLITE_PATH:-}" ] && [ -n "$MCP_JSON" ]; then
    MCP_MEMORY_SQLITE_PATH=$(python3 -c "
import json
with open('$MCP_JSON') as f:
    cfg = json.load(f)
env = cfg.get('mcpServers',{}).get('memory',{}).get('env',{})
print(env.get('MCP_MEMORY_SQLITE_PATH',''))
" 2>/dev/null || true)
    export MCP_MEMORY_SQLITE_PATH
fi

if [ -z "${MCP_MEMORY_SQLITE_PRAGMAS:-}" ] && [ -n "$MCP_JSON" ]; then
    MCP_MEMORY_SQLITE_PRAGMAS=$(python3 -c "
import json
with open('$MCP_JSON') as f:
    cfg = json.load(f)
env = cfg.get('mcpServers',{}).get('memory',{}).get('env',{})
print(env.get('MCP_MEMORY_SQLITE_PRAGMAS',''))
" 2>/dev/null || true)
    export MCP_MEMORY_SQLITE_PRAGMAS
fi

# 락 파일: DB 파일과 같은 디렉토리에 배치 (worktree 간 공유)
if [ -n "${MCP_MEMORY_SQLITE_PATH:-}" ]; then
    LOCK_FILE="$(dirname "$MCP_MEMORY_SQLITE_PATH")/.memory.lock"
else
    LOCK_FILE="$PROJECT_DIR/.agent/data/memory-service/.memory.lock"
fi

# ─────────────────────────────────────────────────────
# 락 파일 정리 (종료/실패 시 항상 제거)
# ─────────────────────────────────────────────────────
cleanup_lock() {
    rm -f "$LOCK_FILE"
}

# ─────────────────────────────────────────────────────
# 락 획득 (최대 10초 대기, 1초 간격 폴링)
# ─────────────────────────────────────────────────────
acquire_lock() {
    mkdir -p "$(dirname "$LOCK_FILE")"
    local retries=0
    while [[ -f "$LOCK_FILE" ]]; do
        # stale lock 감지 (60초 이상이면 강제 제거)
        lock_age=$(( $(date +%s) - $(stat -f %m "$LOCK_FILE" 2>/dev/null || echo 0) ))
        if [[ "$lock_age" -ge 60 ]]; then
            rm -f "$LOCK_FILE"
            break
        fi
        retries=$((retries + 1))
        if [[ "$retries" -ge 10 ]]; then
            echo "mcp-store-memory: lock timeout, skipping" >&2
            return 1
        fi
        sleep 1
    done
    echo $$ > "$LOCK_FILE"
    trap cleanup_lock EXIT
    return 0
}

acquire_lock || exit 1

# JSON escape & CALL_MSG 생성 (python3로 한 번에 처리)
CALL_MSG=$(python3 -c "
import json, sys
title, content, tags_str = sys.argv[1], sys.argv[2], sys.argv[3]
tags = ','.join([t.strip() for t in tags_str.split(',') if t.strip()])
# mcp-memory-service: content에 title을 markdown 헤더로 포함
full_content = '## ' + title + '\n\n' + content
msg = {
    'jsonrpc': '2.0', 'id': 2,
    'method': 'tools/call',
    'params': {
        'name': 'memory_store',
        'arguments': {
            'content': full_content,
            'metadata': {
                'tags': tags,
                'type': 'general'
            }
        }
    }
}
print(json.dumps(msg))
" "$TITLE" "$CONTENT" "$TAGS" 2>/dev/null)

INIT_MSG='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"hook-client","version":"1.0"}}}'
INIT_NOTIFY='{"jsonrpc":"2.0","method":"notifications/initialized"}'

RESPONSE=$(printf '%s\n%s\n%s\n' "$INIT_MSG" "$INIT_NOTIFY" "$CALL_MSG" \
    | MCP_MEMORY_SQLITE_PATH="${MCP_MEMORY_SQLITE_PATH:-}" \
      MCP_MEMORY_SQLITE_PRAGMAS="${MCP_MEMORY_SQLITE_PRAGMAS:-}" \
      timeout 10 memory server 2>/dev/null \
    | grep -m1 '"id":2' || echo "")

if [[ -n "$RESPONSE" ]] && echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if 'result' in d else 1)" 2>/dev/null; then
    exit 0
else
    exit 1
fi
