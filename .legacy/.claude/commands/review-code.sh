#!/bin/sh
# review-code.sh - 코드 리뷰 노트를 CLAUDE.md에 추가하는 스크립트
#
# 목적: 코드 리뷰 시 학습된 내용을 CLAUDE.md에 자동으로 반영합니다.
# GitHub Action과 연계하여 PR 리뷰 코멘트에서 @.claude 태그를 감지하면
# 이 스크립트를 호출하여 지식을 복리로 축적합니다.
#
# 사용법: /review-code [PR 번호] [리뷰 노트]
#
# POSIX 표준을 준수하여 다양한 환경에서 동작하도록 작성되었습니다.

set -e

# 색상 출력을 위한 함수
if [ -t 1 ]; then
	RED='\033[0;31m'
	GREEN='\033[0;32m'
	YELLOW='\033[1;33m'
	BLUE='\033[0;34m'
	NC='\033[0m'
else
	RED=''
	GREEN=''
	YELLOW=''
	BLUE=''
	NC=''
fi

# 인자 처리
PR_NUMBER="${1:-local}"
REVIEW_NOTES="${2:-Code review completed}"

# 날짜 형식 (POSIX 호환)
CURRENT_DATE=$(date +%Y-%m-%d 2>/dev/null || date +%Y-%m-%d)

echo "${BLUE}📝 [REVIEW] Updating CLAUDE.md with review insights...${NC}"

# 프로젝트 루트 찾기
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)
CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"

# CLAUDE.md 존재 확인
if [ ! -f "$CLAUDE_MD" ]; then
	echo "${RED}❌ Error: CLAUDE.md not found at $CLAUDE_MD${NC}"
	exit 1
fi

# 마커 위치 찾기
MARKER_START="<!-- CODE_REVIEW_UPDATES_START -->"
MARKER_END="<!-- CODE_REVIEW_UPDATES_END -->"

# 마커가 존재하는지 확인
if ! grep -q "$MARKER_START" "$CLAUDE_MD"; then
	echo "${RED}❌ Error: CODE_REVIEW_UPDATES_START marker not found in CLAUDE.md${NC}"
	echo "${YELLOW}   Please ensure the marker exists in the Code Review Updates section.${NC}"
	exit 1
fi

# 임시 파일 생성
TEMP_FILE=$(mktemp)

# 마커 시작 전까지 복사
awk -v marker="$MARKER_START" '
	$0 ~ marker { 
		print $0
		print ""
		print "- **PR #'$PR_NUMBER'** ('$CURRENT_DATE'): '$REVIEW_NOTES'"
		next
	}
	{ print }
' "$CLAUDE_MD" > "$TEMP_FILE"

# 원본 파일로 교체
mv "$TEMP_FILE" "$CLAUDE_MD"

echo "${GREEN}✅ [REVIEW] CLAUDE.md updated successfully!${NC}"
echo "   Added: PR #$PR_NUMBER - $REVIEW_NOTES"

