#!/bin/sh
# commit-push-pr.sh - Git 컨벤션 강제 PR 자동화
#
# 목적: Git 컨벤션을 엄격히 적용하여 PR을 자동화합니다.
# 사내 표준에 따라 브랜치명에서 이슈 번호를 추출하고,
# 커밋 메시지 형식을 강제하며, Squash merge를 유도합니다.
#
# 사용법:
#   scripts/core/commit-push-pr.sh [DESCRIPTION]
#   또는
#   .claude/commands/commit-push-pr.sh [DESCRIPTION]
#
# Git 컨벤션 (팀 표준):
#   - 브랜치명: feature/{issue_number}-{description} 또는 bugfix/{issue_number}-{description}
#   - 커밋 메시지: "Resolved #{ISSUE_NUMBER} - {DESCRIPTION}" (정확한 형식 강제)
#   - PR: feature/bugfix 브랜치 → develop (반드시 Squash and merge)
#   - 이슈 선행 생성 필수: 모든 변경사항은 먼저 GitHub Issue를 생성해야 함
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

echo "${BLUE}🚀 [Git Convention PR] Starting PR automation...${NC}"

# 1. 현재 브랜치명에서 이슈 번호 추출
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ -z "$CURRENT_BRANCH" ]; then
	echo "${RED}❌ Error: Not in a git repository or no branch checked out.${NC}"
	exit 1
fi

echo "${BLUE}📋 Current branch: ${GREEN}$CURRENT_BRANCH${NC}"

# 브랜치명 패턴 매칭: feature/{issue_number}-{description} 또는 bugfix/{issue_number}-{description}
# 팀 표준: 브랜치명은 반드시 이 형식을 따라야 하며, 위반 시 스크립트가 종료됨
ISSUE_NUMBER=""
BRANCH_PREFIX=""
DESCRIPTION=""

# POSIX sh에서 정규식 매칭 (sed 사용)
BRANCH_PATTERN=$(echo "$CURRENT_BRANCH" | sed -n 's/^\(feature\|bugfix\)\/\([0-9]\+\)-\(.*\)$/\1|\2|\3/p')

if [ -n "$BRANCH_PATTERN" ]; then
	# 패턴이 매칭된 경우 파싱
	BRANCH_PREFIX=$(echo "$BRANCH_PATTERN" | cut -d'|' -f1)
	ISSUE_NUMBER=$(echo "$BRANCH_PATTERN" | cut -d'|' -f2)
	DESCRIPTION=$(echo "$BRANCH_PATTERN" | cut -d'|' -f3)
else
	# 패턴이 매칭되지 않은 경우: 팀 표준 위반으로 스크립트 종료
	echo "${RED}❌ Error: Branch name does not follow team convention.${NC}"
	echo "${RED}   Required format: feature/{issue_number}-{description} or bugfix/{issue_number}-{description}${NC}"
	echo "${RED}   Example: feature/50-cli-command-support-specific-page${NC}"
	echo ""
	echo "${YELLOW}💡 [Team Standard]${NC}"
	echo "${YELLOW}   1. Create GitHub Issue first (required)${NC}"
	echo "${YELLOW}   2. Create branch from Issue using 'Development > Create a branch'${NC}"
	echo "${YELLOW}   3. Use branch prefix: 'feature' for new features, 'bugfix' for bug fixes${NC}"
	echo ""
	echo "${YELLOW}   To fix: git branch -m feature/{issue_number}-{description}${NC}"
	exit 1
fi

# 2. 브랜치 접두사 검증
if [ -z "$BRANCH_PREFIX" ]; then
	if [ -z "$ISSUE_NUMBER" ]; then
		echo "${RED}❌ Error: Cannot determine issue number from branch name.${NC}"
		echo "${RED}   Branch name must follow: feature/{issue_number}-{description} or bugfix/{issue_number}-{description}${NC}"
		exit 1
	fi
	# 접두사가 없지만 이슈 번호는 있는 경우 (수동 입력)
	BRANCH_PREFIX="feature"  # 기본값
fi

# 3. 커밋 메시지 생성
if [ -z "$ISSUE_NUMBER" ]; then
	echo "${RED}❌ Error: Issue number is required but could not be extracted.${NC}"
	exit 1
fi

# DESCRIPTION이 비어있으면 사용자 입력 또는 브랜치명에서 추출
if [ -z "$DESCRIPTION" ]; then
	if [ -n "$1" ]; then
		DESCRIPTION="$1"
	else
		# 브랜치명에서 마지막 부분 추출
		DESCRIPTION=$(echo "$CURRENT_BRANCH" | sed 's/.*-//')
		if [ -z "$DESCRIPTION" ] || [ "$DESCRIPTION" = "$CURRENT_BRANCH" ]; then
			DESCRIPTION="Update"
		fi
	fi
fi

# 커밋 메시지 형식: "Resolved #{ISSUE_NUMBER} - {DESCRIPTION}" (팀 표준 강제)
# 주의: "Resovled"가 아닌 "Resolved"로 정확히 작성해야 함
COMMIT_MSG="Resolved #$ISSUE_NUMBER - $DESCRIPTION"

echo "${BLUE}📝 Commit message: ${GREEN}$COMMIT_MSG${NC}"

# Git 상태 확인
if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
	echo "${YELLOW}⚠️  No changes to commit.${NC}"
	exit 0
fi

# 변경된 파일 목록 표시
CHANGED_FILES=$(git diff --name-only 2>/dev/null | head -10 || echo "none")
echo "${BLUE}📋 Changed files:${NC}"
echo "$CHANGED_FILES" | while read -r file; do
	if [ -n "$file" ]; then
		echo "   - $file"
	fi
done

# 변경 통계
STATS=$(git diff --stat 2>/dev/null | tail -1 || echo "No changes")
echo "${BLUE}📊 Stats: $STATS${NC}"

# 4. 커밋 및 푸시
echo "${BLUE}📦 Staging changes...${NC}"
git add .

echo "${BLUE}💾 Creating commit: ${GREEN}$COMMIT_MSG${NC}"
git commit -m "$COMMIT_MSG"

echo "${BLUE}📤 Pushing to remote...${NC}"
git push origin "$CURRENT_BRANCH" || {
	echo "${RED}❌ Push failed. Please check your git configuration.${NC}"
	exit 1
}

# 5. PR 생성 (gh CLI 사용)
if ! command -v gh >/dev/null 2>&1; then
	echo "${YELLOW}⚠️  GitHub CLI (gh) not found.${NC}"
	echo "${YELLOW}   Install it with: brew install gh (macOS) or visit https://cli.github.com${NC}"
	echo "${YELLOW}   Please create PR manually:${NC}"
	echo "${YELLOW}   Branch: $CURRENT_BRANCH${NC}"
	echo "${YELLOW}   Base: develop${NC}"
	exit 0
fi

# gh CLI 인증 확인
if ! gh auth status >/dev/null 2>&1; then
	echo "${YELLOW}⚠️  GitHub CLI not authenticated.${NC}"
	echo "${YELLOW}   Run: gh auth login${NC}"
	echo "${YELLOW}   Please create PR manually:${NC}"
	echo "${YELLOW}   Branch: $CURRENT_BRANCH${NC}"
	echo "${YELLOW}   Base: develop${NC}"
	exit 0
fi

echo "${BLUE}🔗 Creating pull request...${NC}"

# 기본 브랜치 감지 (feature/bugfix 브랜치인 경우 develop, 그 외는 main)
BASE_BRANCH="develop"
if [ "$BRANCH_PREFIX" != "feature" ] && [ "$BRANCH_PREFIX" != "bugfix" ]; then
	# develop → main PR인 경우
	BASE_BRANCH=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
fi

# PR 본문 생성
PR_BODY="Auto-generated PR from AI workflow

## Changes
\`\`\`
$STATS
\`\`\`

## Files Changed
\`\`\`
$CHANGED_FILES
\`\`\`

## Git Convention
- Branch: \`$CURRENT_BRANCH\`
- Issue: #$ISSUE_NUMBER
- Commit: \`$COMMIT_MSG\`
"

# PR 생성
if gh pr create \
	--title "$COMMIT_MSG" \
	--body "$PR_BODY" \
	--base "$BASE_BRANCH" 2>&1; then
	echo "${GREEN}✅ Pull request created successfully!${NC}"
	
	# Squash and merge 유도 메시지 출력
	if [ "$BRANCH_PREFIX" = "feature" ] || [ "$BRANCH_PREFIX" = "bugfix" ]; then
		echo ""
		echo "${BLUE}💡 [Git Convention] Important:${NC}"
		echo "${YELLOW}   When merging this PR, please use 'Squash and merge' option.${NC}"
		echo "${YELLOW}   This ensures a clean commit history on the develop branch.${NC}"
	fi
else
	echo "${YELLOW}⚠️  PR creation failed. You may need to create it manually.${NC}"
	echo "${YELLOW}   Branch: $CURRENT_BRANCH${NC}"
	echo "${YELLOW}   Base: $BASE_BRANCH${NC}"
	exit 0
fi

