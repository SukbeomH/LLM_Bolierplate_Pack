#!/bin/sh
# commit-push-pr.sh - PR 자동화 스크립트 (토큰 최적화)
#
# 목적: 작업 완료 후 코드를 커밋하고 PR을 생성하는 과정을 자동화합니다.
# 토큰 최적화를 위해 인라인 bash로 정보를 미리 계산하여
# AI와의 불필요한 왕복을 방지합니다.
#
# 사용법: /commit-push-pr [커밋 메시지]
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

# 커밋 메시지 처리 (기본값 제공)
COMMIT_MSG="${1:-Auto-commit: $(date +%Y-%m-%d\ %H:%M:%S)}"

echo "${BLUE}🚀 [PR] Preparing to create PR...${NC}"

# 인라인 bash로 정보 사전 계산 (토큰 절약)
# 이 정보들을 미리 계산하여 AI에게 전달하면 모델이 탐색할 필요가 없습니다.

echo "📋 Pre-calculating git information..."

# 현재 브랜치 정보
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
echo "   Current branch: ${GREEN}$CURRENT_BRANCH${NC}"

# 변경된 파일 목록
CHANGED_FILES=$(git diff --name-only 2>/dev/null | head -10 || echo "none")
echo "   Changed files:"
echo "$CHANGED_FILES" | while read -r file; do
	if [ -n "$file" ]; then
		echo "     - $file"
	fi
done

# 변경 통계
STATS=$(git diff --stat 2>/dev/null | tail -1 || echo "No changes")
echo "   Stats: $STATS"

# 원격 저장소 확인
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "no remote")
echo "   Remote: $REMOTE_URL"

# gh CLI 확인
if ! command -v gh >/dev/null 2>&1; then
	echo "${YELLOW}⚠️  Warning: GitHub CLI (gh) not found.${NC}"
	echo "${YELLOW}   Install it with: brew install gh (macOS) or visit https://cli.github.com${NC}"
	echo "${YELLOW}   Continuing with git operations only...${NC}"
	GH_AVAILABLE=false
else
	GH_AVAILABLE=true
	# gh CLI 인증 확인
	if ! gh auth status >/dev/null 2>&1; then
		echo "${YELLOW}⚠️  Warning: GitHub CLI not authenticated.${NC}"
		echo "${YELLOW}   Run: gh auth login${NC}"
		GH_AVAILABLE=false
	fi
fi

# Git 상태 확인
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
	echo "${YELLOW}⚠️  No changes to commit.${NC}"
	exit 0
fi

# 변경사항 스테이징
echo "${BLUE}📦 Staging changes...${NC}"
git add .

# 커밋 생성
echo "${BLUE}💾 Creating commit: ${NC}${GREEN}$COMMIT_MSG${NC}"
git commit -m "$COMMIT_MSG"

# 푸시
echo "${BLUE}📤 Pushing to remote...${NC}"
git push origin "$CURRENT_BRANCH" || {
	echo "${RED}❌ Push failed. Please check your git configuration.${NC}"
	exit 1
}

# PR 생성 (gh CLI가 사용 가능한 경우)
if [ "$GH_AVAILABLE" = true ]; then
	echo "${BLUE}🔗 Creating pull request...${NC}"
	
	# 기본 브랜치 감지 (보통 main 또는 develop)
	DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
	
	gh pr create \
		--title "$COMMIT_MSG" \
		--body "Auto-generated PR from AI workflow

## Changes
\`\`\`
$STATS
\`\`\`

## Files Changed
\`\`\`
$CHANGED_FILES
\`\`\`
" \
		--base "$DEFAULT_BRANCH" || {
		echo "${YELLOW}⚠️  PR creation failed. You may need to create it manually.${NC}"
		exit 0
	}
	
	echo "${GREEN}✅ [PR] Pull request created successfully!${NC}"
else
	echo "${YELLOW}⚠️  GitHub CLI not available. Please create PR manually.${NC}"
	echo "${YELLOW}   Branch: $CURRENT_BRANCH${NC}"
fi

