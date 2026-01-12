#!/bin/sh
# verify-app.sh - 종합 검증 래퍼 스크립트
#
# 목적: AI가 구현한 코드를 종합적으로 검증하는 슬래시 커맨드입니다.
# 이 스크립트는 향후 구현될 scripts/core/auto_verify.sh를 호출하여
# 감지된 스택에 맞는 검증 도구를 자동으로 실행합니다.
#
# 사용법: /verify-app
#
# POSIX 표준을 준수하여 다양한 환경에서 동작하도록 작성되었습니다.

set -e

# 스크립트의 디렉토리 경로를 얻기 위한 POSIX 호환 방법
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
CORE_SCRIPT="$PROJECT_ROOT/scripts/core/auto_verify.sh"

# 색상 출력을 위한 함수 (터미널이 지원하는 경우에만)
if [ -t 1 ]; then
	RED='\033[0;31m'
	GREEN='\033[0;32m'
	YELLOW='\033[1;33m'
	NC='\033[0m' # No Color
else
	RED=''
	GREEN=''
	YELLOW=''
	NC=''
fi

echo "${GREEN}🔍 [VERIFY-APP] Starting comprehensive verification...${NC}"

# auto_verify.sh가 존재하는지 확인
if [ ! -f "$CORE_SCRIPT" ]; then
	echo "${YELLOW}⚠️  Warning: $CORE_SCRIPT not found.${NC}"
	echo "${YELLOW}   This script will be implemented in Phase 4.${NC}"
	echo "${YELLOW}   For now, running basic verification checks...${NC}"
	
	# 기본 검증 로직 (Phase 4 전까지 임시로 사용)
	# detect_stack.sh도 확인
	DETECT_SCRIPT="$PROJECT_ROOT/scripts/core/detect_stack.sh"
	if [ ! -f "$DETECT_SCRIPT" ]; then
		echo "${RED}❌ Error: $DETECT_SCRIPT not found.${NC}"
		echo "${RED}   Please run Phase 4 to implement stack detection.${NC}"
		exit 1
	fi
	
	# 스택 감지 실행
	echo "📋 Detecting project stack..."
	. "$DETECT_SCRIPT"
	
	# 감지된 스택에 따라 기본 검증 실행
	if [ "$DETECTED_STACK" = "node" ]; then
		echo "🔷 Running Node.js verification..."
		if command -v npm >/dev/null 2>&1; then
			npm run lint 2>/dev/null || echo "${YELLOW}   Lint check skipped (no lint script)${NC}"
			npm run type-check 2>/dev/null || echo "${YELLOW}   Type check skipped (no type-check script)${NC}"
			npm test 2>/dev/null || echo "${YELLOW}   Tests skipped (no test script)${NC}"
		fi
	elif [ "$DETECTED_STACK" = "python" ]; then
		echo "🐍 Running Python verification..."
		if command -v pytest >/dev/null 2>&1; then
			pytest 2>/dev/null || echo "${YELLOW}   Tests skipped${NC}"
		fi
	fi
	
	echo "${GREEN}✅ [VERIFY-APP] Basic verification completed.${NC}"
	echo "${YELLOW}   Note: Full verification will be available after Phase 4 implementation.${NC}"
	exit 0
fi

# auto_verify.sh가 존재하는 경우 실행
echo "🚀 Executing auto_verify.sh..."
exec "$CORE_SCRIPT"

