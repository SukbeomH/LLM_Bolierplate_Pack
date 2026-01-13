#!/bin/sh
# migrate_to_uv.sh - Poetry 프로젝트를 uv로 자동 마이그레이션
#
# 목적: pyenv와 poetry를 사용하는 프로젝트를 감지하여 uv 기반의 AI-Native 환경으로 자동 전환합니다.
#
# 사용법:
#   scripts/core/migrate_to_uv.sh [프로젝트 경로]
#
# 워크플로우:
#   1. poetry.lock 감지
#   2. pyproject.toml에서 Python 버전 파싱
#   3. uv python install 실행
#   4. uv sync로 uv.lock과 .venv 생성
#   5. 성공 시 기존 파일 백업 (.bak)
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

# 프로젝트 루트 디렉토리 찾기
TARGET_DIR="${1:-$(pwd)}"
TARGET_DIR=$(cd "$TARGET_DIR" && pwd)

echo "${BLUE}🔄 [UV Migration] Starting migration from Poetry to uv...${NC}"

# 1. poetry.lock 감지
echo "${BLUE}1. Checking for poetry.lock...${NC}"
POETRY_LOCK="$TARGET_DIR/poetry.lock"
PYPROJECT_TOML="$TARGET_DIR/pyproject.toml"

if [ ! -f "$POETRY_LOCK" ]; then
	echo "${YELLOW}   ⚠️  poetry.lock not found. Skipping migration.${NC}"
	exit 0
fi

if [ ! -f "$PYPROJECT_TOML" ]; then
	echo "${RED}   ❌ pyproject.toml not found. Cannot proceed with migration.${NC}"
	exit 1
fi

echo "${GREEN}   ✅ poetry.lock found${NC}"

# 2. uv 설치 여부 확인
echo "${BLUE}2. Checking uv installation...${NC}"
if ! command -v uv >/dev/null 2>&1; then
	echo "${YELLOW}   ⚠️  uv is not installed${NC}"
	echo "${YELLOW}   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
	echo "${YELLOW}   Or visit: https://github.com/astral-sh/uv${NC}"
	exit 1
fi

UV_VERSION=$(uv --version 2>/dev/null || echo "unknown")
echo "${GREEN}   ✅ uv is installed (${UV_VERSION})${NC}"

# 3. pyproject.toml에서 Python 버전 파싱
echo "${BLUE}3. Parsing Python version from pyproject.toml...${NC}"
PYTHON_VERSION=""

# pyproject.toml에서 Python 버전 추출 (requires-python 또는 python 필드)
if command -v grep >/dev/null 2>&1; then
	# requires-python 필드 찾기 (예: requires-python = ">=3.11,<4.0")
	REQUIRES_PYTHON=$(grep -E '^requires-python\s*=' "$PYPROJECT_TOML" 2>/dev/null | head -1 | sed 's/.*=\s*"\([^"]*\)".*/\1/' | sed "s/.*=\s*'\([^']*\)'.*/\1/" || echo "")
	
	# python 필드 찾기 (예: python = "^3.11")
	PYTHON_FIELD=$(grep -E '^python\s*=' "$PYPROJECT_TOML" 2>/dev/null | head -1 | sed 's/.*=\s*"\([^"]*\)".*/\1/' | sed "s/.*=\s*'\([^']*\)'.*/\1/" || echo "")
	
	# 버전 범위에서 최소 버전 추출
	if [ -n "$REQUIRES_PYTHON" ]; then
		PYTHON_VERSION=$(echo "$REQUIRES_PYTHON" | sed 's/[^0-9.]*\([0-9]\+\.[0-9]\+\).*/\1/' | head -1)
	elif [ -n "$PYTHON_FIELD" ]; then
		PYTHON_VERSION=$(echo "$PYTHON_FIELD" | sed 's/[^0-9.]*\([0-9]\+\.[0-9]\+\).*/\1/' | head -1)
	fi
fi

if [ -z "$PYTHON_VERSION" ]; then
	echo "${YELLOW}   ⚠️  Could not parse Python version from pyproject.toml${NC}"
	echo "${YELLOW}   Using default: 3.11${NC}"
	PYTHON_VERSION="3.11"
else
	echo "${GREEN}   ✅ Detected Python version: ${PYTHON_VERSION}${NC}"
fi

# 4. uv python install 실행
echo "${BLUE}4. Installing Python ${PYTHON_VERSION} with uv...${NC}"
if uv python install "$PYTHON_VERSION" 2>&1; then
	echo "${GREEN}   ✅ Python ${PYTHON_VERSION} installed${NC}"
else
	echo "${RED}   ❌ Failed to install Python ${PYTHON_VERSION}${NC}"
	exit 1
fi

# 5. uv sync 실행 (uv.lock과 .venv 생성)
echo "${BLUE}5. Running uv sync to create uv.lock and .venv...${NC}"
cd "$TARGET_DIR"

# 기존 .venv가 있으면 백업
if [ -d ".venv" ]; then
	echo "${YELLOW}   ⚠️  Existing .venv found. Backing up...${NC}"
	mv .venv .venv.poetry.bak
fi

# uv sync 실행
if uv sync 2>&1; then
	echo "${GREEN}   ✅ uv sync completed successfully${NC}"
	echo "${GREEN}   ✅ uv.lock created${NC}"
	echo "${GREEN}   ✅ .venv created${NC}"
else
	echo "${RED}   ❌ uv sync failed${NC}"
	# 백업된 .venv 복구
	if [ -d ".venv.poetry.bak" ]; then
		echo "${YELLOW}   Restoring .venv backup...${NC}"
		mv .venv.poetry.bak .venv
	fi
	exit 1
fi

# 6. 기존 파일 백업 (.bak)
echo "${BLUE}6. Backing up existing files...${NC}"
BACKUP_SUFFIX=".poetry.bak.$(date +%Y%m%d_%H%M%S)"

if [ -f "$POETRY_LOCK" ]; then
	mv "$POETRY_LOCK" "${POETRY_LOCK}${BACKUP_SUFFIX}"
	echo "${GREEN}   ✅ poetry.lock backed up to ${POETRY_LOCK}${BACKUP_SUFFIX}${NC}"
fi

if [ -f "$TARGET_DIR/.python-version" ]; then
	mv "$TARGET_DIR/.python-version" "${TARGET_DIR}/.python-version${BACKUP_SUFFIX}"
	echo "${GREEN}   ✅ .python-version backed up${NC}"
fi

# 7. 마이그레이션 완료 메시지
echo ""
echo "${GREEN}✅ Migration completed successfully!${NC}"
echo ""
echo "${BLUE}📋 Migration Summary:${NC}"
echo "   - Python ${PYTHON_VERSION} installed via uv"
echo "   - uv.lock created"
echo "   - .venv created"
echo "   - poetry.lock backed up"
if [ -f "$TARGET_DIR/.python-version${BACKUP_SUFFIX}" ]; then
	echo "   - .python-version backed up"
fi
echo ""
echo "${YELLOW}💡 Next steps:${NC}"
echo "   1. Test your project: uv run python -m pytest"
echo "   2. Run your app: uv run python main.py"
echo "   3. If issues occur, restore backups:"
echo "      - mv ${POETRY_LOCK}${BACKUP_SUFFIX} poetry.lock"
if [ -f "$TARGET_DIR/.python-version${BACKUP_SUFFIX}" ]; then
	echo "      - mv ${TARGET_DIR}/.python-version${BACKUP_SUFFIX} .python-version"
fi
echo "   4. Remove uv files: rm -rf uv.lock .venv"
echo ""

