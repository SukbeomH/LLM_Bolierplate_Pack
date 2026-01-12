#!/bin/sh
# check_env.sh - 환경 변수 자가 진단 및 MCP 연계
#
# 목적: .env_sample과 .env를 비교하여 누락된 환경 변수를 감지합니다.
# 검증 실패 시 Codanna/Serena MCP를 사용하여 소스 코드 내 환경 변수 사용처를
# 정밀 분석할 수 있도록 제안합니다.
#
# 사용법:
#   scripts/core/check_env.sh
#
# 보안:
#   - .env의 실제 값은 절대 로그에 노출하지 않습니다.
#   - KEY 이름만 비교하여 누락 여부를 확인합니다.
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
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)

ENV_SAMPLE="$PROJECT_ROOT/.env_sample"
ENV_FILE="$PROJECT_ROOT/.env"

echo "${BLUE}🔍 [Environment Check] Checking environment variables...${NC}"

# 1. .env_sample 파일 읽기
if [ ! -f "$ENV_SAMPLE" ]; then
	echo "${YELLOW}⚠️  .env_sample file not found at $ENV_SAMPLE${NC}"
	echo "${YELLOW}   Skipping environment variable check.${NC}"
	exit 0
fi

echo "${BLUE}📋 Reading .env_sample...${NC}"

# .env_sample에서 KEY 목록 추출 (KEY=VALUE 형식 파싱)
# 주석(#)과 빈 줄 제외, KEY만 추출
ENV_SAMPLE_KEYS=""
while IFS= read -r line || [ -n "$line" ]; do
	# 주석 제거
	line=$(echo "$line" | sed 's/#.*$//')
	# 앞뒤 공백 제거
	line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
	# 빈 줄 건너뛰기
	if [ -z "$line" ]; then
		continue
	fi
	# KEY=VALUE 형식에서 KEY만 추출
	key=$(echo "$line" | sed 's/=.*$//' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
	if [ -n "$key" ]; then
		if [ -z "$ENV_SAMPLE_KEYS" ]; then
			ENV_SAMPLE_KEYS="$key"
		else
			ENV_SAMPLE_KEYS="$ENV_SAMPLE_KEYS
$key"
		fi
	fi
done < "$ENV_SAMPLE"

if [ -z "$ENV_SAMPLE_KEYS" ]; then
	echo "${YELLOW}⚠️  No environment variables found in .env_sample${NC}"
	exit 0
fi

ENV_SAMPLE_COUNT=$(echo "$ENV_SAMPLE_KEYS" | grep -c . || echo "0")
echo "${GREEN}   Found $ENV_SAMPLE_COUNT environment variable(s) in .env_sample${NC}"

# 2. .env 파일 읽기 (존재하는 경우)
ENV_KEYS=""
MISSING_KEYS=""

if [ ! -f "$ENV_FILE" ]; then
	echo "${YELLOW}⚠️  .env file not found at $ENV_FILE${NC}"
	echo "${YELLOW}   All environment variables from .env_sample are missing.${NC}"
	MISSING_KEYS="$ENV_SAMPLE_KEYS"
else
	echo "${BLUE}📋 Reading .env...${NC}"
	
	# .env에서 KEY 목록 추출 (실제 값은 로그에 노출하지 않음)
	while IFS= read -r line || [ -n "$line" ]; do
		# 주석 제거
		line=$(echo "$line" | sed 's/#.*$//')
		# 앞뒤 공백 제거
		line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
		# 빈 줄 건너뛰기
		if [ -z "$line" ]; then
			continue
		fi
		# KEY=VALUE 형식에서 KEY만 추출
		key=$(echo "$line" | sed 's/=.*$//' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
		if [ -n "$key" ]; then
			if [ -z "$ENV_KEYS" ]; then
				ENV_KEYS="$key"
			else
				ENV_KEYS="$ENV_KEYS
$key"
			fi
		fi
	done < "$ENV_FILE"
	
	ENV_COUNT=$(echo "$ENV_KEYS" | grep -c . || echo "0")
	echo "${GREEN}   Found $ENV_COUNT environment variable(s) in .env${NC}"
	
	# 3. 누락된 KEY 감지
	echo "${BLUE}🔍 Comparing .env_sample and .env...${NC}"
	
	# .env_sample에 있지만 .env에 없는 KEY 찾기
	while IFS= read -r sample_key || [ -n "$sample_key" ]; do
		if [ -z "$sample_key" ]; then
			continue
		fi
		# .env에 해당 KEY가 있는지 확인
		found=false
		while IFS= read -r env_key || [ -n "$env_key" ]; do
			if [ "$sample_key" = "$env_key" ]; then
				found=true
				break
			fi
		done <<EOF
$ENV_KEYS
EOF
		
		if [ "$found" = false ]; then
			if [ -z "$MISSING_KEYS" ]; then
				MISSING_KEYS="$sample_key"
			else
				MISSING_KEYS="$MISSING_KEYS
$sample_key"
			fi
		fi
	done <<EOF
$ENV_SAMPLE_KEYS
EOF
fi

# 4. 누락된 KEY가 있는 경우 처리
if [ -n "$MISSING_KEYS" ]; then
	MISSING_COUNT=$(echo "$MISSING_KEYS" | grep -c . || echo "0")
	echo ""
	echo "${RED}❌ Found $MISSING_COUNT missing environment variable(s):${NC}"
	echo "$MISSING_KEYS" | while read -r key; do
		if [ -n "$key" ]; then
			echo "${RED}   - $key${NC}"
		fi
	done
	
	echo ""
	echo "${YELLOW}💡 [MCP Integration] To find where these environment variables are used:${NC}"
	echo "${BLUE}   1. Use Codanna MCP semantic search:${NC}"
	# 보안: KEY 이름만 출력하고, 여러 KEY가 있는 경우 첫 번째만 예시로 표시
	FIRST_MISSING_KEY=$(echo "$MISSING_KEYS" | head -1)
	echo "${BLUE}      Query: 'Where is $FIRST_MISSING_KEY used in the codebase?'${NC}"
	echo "${BLUE}   2. Use Serena MCP find_symbol:${NC}"
	echo "${BLUE}      Search for: 'process.env.$FIRST_MISSING_KEY' or 'os.getenv(\"$FIRST_MISSING_KEY\")'${NC}"
	
	echo ""
	echo "${YELLOW}💡 [Action Required]${NC}"
	echo "${YELLOW}   Add missing environment variables to .env file.${NC}"
	echo "${YELLOW}   You can copy from .env_sample and update the values.${NC}"
	
	# .env_sample의 기본값을 .env에 추가할지 물어봄 (비대화형 모드에서는 건너뜀)
	if [ -t 0 ]; then
		echo ""
		echo "${YELLOW}   Copy missing variables from .env_sample to .env? (y/N):${NC}"
		read -r response || true
		if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
			echo "${BLUE}   Copying missing variables...${NC}"
			# .env_sample에서 누락된 KEY의 라인을 찾아 .env에 추가
			while IFS= read -r key || [ -n "$key" ]; do
				if [ -z "$key" ]; then
					continue
				fi
				# .env_sample에서 해당 KEY의 전체 라인 찾기
				# 보안: grep 결과를 변수에 저장하여 값이 로그에 노출되지 않도록 함
				sample_line=$(grep "^$key=" "$ENV_SAMPLE" 2>/dev/null | head -1 || echo "")
				if [ -n "$sample_line" ]; then
					# .env에 추가 (이미 있는지 확인)
					# 보안: grep -q를 사용하여 매칭 결과만 확인하고 값은 출력하지 않음
					if ! grep -q "^$key=" "$ENV_FILE" 2>/dev/null; then
						# 보안: echo로 파일에 추가할 때도 값이 터미널에 출력되지 않도록 리다이렉션만 사용
						echo "$sample_line" >> "$ENV_FILE" 2>/dev/null
						# KEY 이름만 출력 (값은 절대 출력하지 않음)
						echo "${GREEN}   Added: $key${NC}"
					fi
				fi
			done <<EOF
$MISSING_KEYS
EOF
			echo "${GREEN}✅ Missing variables copied to .env${NC}"
			echo "${YELLOW}   Please update the values in .env file.${NC}"
		fi
	fi
	
	exit 1
else
	echo ""
	echo "${GREEN}✅ All environment variables from .env_sample are present in .env${NC}"
	exit 0
fi

