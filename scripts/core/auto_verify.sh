#!/bin/sh
# auto_verify.sh - 규정 준수형 자동 검증 및 환경 설정
#
# 목적: detect_stack.sh 결과를 기반으로 스택별 검증을 수행합니다.
# 사내 Quality 도구(ruff, pre-commit)를 자동 실행하여 코드 품질을 보장합니다.
#
# 사용법:
#   scripts/core/auto_verify.sh
#   또는
#   mise run verify
#
# 검증 순서:
#   1. 포매팅 (ruff format, prettier 등)
#   2. 린팅 (ruff check, eslint 등)
#   3. 타입 체크 (mypy, tsc 등)
#   4. 테스트 (pytest, jest 등)
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

# 검증 결과 추적
VERIFICATION_FAILED=0
VERIFICATION_ERRORS=""

# 에러 메시지 추가 함수
add_error() {
	VERIFICATION_FAILED=1
	if [ -z "$VERIFICATION_ERRORS" ]; then
		VERIFICATION_ERRORS="$1"
	else
		VERIFICATION_ERRORS="$VERIFICATION_ERRORS\n$1"
	fi
}

echo "${BLUE}🔍 [Auto Verify] Starting verification process...${NC}"

# 1. 스택 감지 스크립트를 source하여 환경 변수 로드
if [ -f "$SCRIPT_DIR/detect_stack.sh" ]; then
	. "$SCRIPT_DIR/detect_stack.sh"
else
	echo "${RED}❌ Error: detect_stack.sh not found at $SCRIPT_DIR/detect_stack.sh${NC}"
	exit 1
fi

# 스택이 감지되지 않은 경우 종료
if [ -z "$DETECTED_STACK" ]; then
	echo "${RED}❌ Error: Stack detection failed. Cannot proceed with verification.${NC}"
	exit 1
fi

echo "${BLUE}📋 [Auto Verify] Detected stack: $DETECTED_STACK (Package Manager: $DETECTED_PACKAGE_MANAGER)${NC}"

# 2. 스택별 검증 실행
case "$DETECTED_STACK" in
	python)
		echo "${BLUE}🐍 [Python/Poetry] Running Python-specific verification...${NC}"
		
		# 2a. Poetry shell 활성화 확인
		if [ -z "$VIRTUAL_ENV" ] && [ -n "$DETECTED_VENV_PATH" ]; then
			if [ -d "$PROJECT_ROOT/$DETECTED_VENV_PATH" ]; then
				echo "${YELLOW}⚠️  Virtual environment not activated. Activating...${NC}"
				# POSIX sh에서는 source를 사용하여 가상 환경 활성화
				if [ -f "$PROJECT_ROOT/$DETECTED_VENV_PATH/bin/activate" ]; then
					. "$PROJECT_ROOT/$DETECTED_VENV_PATH/bin/activate"
					echo "${GREEN}✅ Virtual environment activated${NC}"
				fi
			fi
		fi
		
		# Poetry 명령어 확인
		if ! command -v poetry >/dev/null 2>&1; then
			echo "${YELLOW}⚠️  Poetry not found in PATH. Some checks may be skipped.${NC}"
		fi
		
		# 2b. ruff check 실행 (black, mypy는 deprecated)
		if command -v ruff >/dev/null 2>&1; then
			echo "${BLUE}   Running ruff check...${NC}"
			if ruff check "$PROJECT_ROOT" 2>&1; then
				echo "${GREEN}   ✅ ruff check passed${NC}"
			else
				add_error "ruff check failed"
				echo "${RED}   ❌ ruff check failed${NC}"
			fi
		elif [ -f "$PROJECT_ROOT/.venv/bin/ruff" ] || [ -f "$PROJECT_ROOT/venv/bin/ruff" ]; then
			# 가상 환경 내 ruff 사용
			RUFF_CMD=""
			if [ -f "$PROJECT_ROOT/.venv/bin/ruff" ]; then
				RUFF_CMD="$PROJECT_ROOT/.venv/bin/ruff"
			elif [ -f "$PROJECT_ROOT/venv/bin/ruff" ]; then
				RUFF_CMD="$PROJECT_ROOT/venv/bin/ruff"
			fi
			if [ -n "$RUFF_CMD" ]; then
				echo "${BLUE}   Running ruff check (from venv)...${NC}"
				if "$RUFF_CMD" check "$PROJECT_ROOT" 2>&1; then
					echo "${GREEN}   ✅ ruff check passed${NC}"
				else
					add_error "ruff check failed"
					echo "${RED}   ❌ ruff check failed${NC}"
				fi
			fi
		else
			echo "${YELLOW}   ⚠️  ruff not found. Install with: poetry add ruff --group dev${NC}"
		fi
		
		# 2c. ruff format 실행
		if command -v ruff >/dev/null 2>&1; then
			echo "${BLUE}   Running ruff format...${NC}"
			if ruff format --check "$PROJECT_ROOT" 2>&1; then
				echo "${GREEN}   ✅ ruff format check passed${NC}"
			else
				echo "${YELLOW}   ⚠️  Code formatting issues detected. Run 'ruff format' to fix.${NC}"
				# 포매팅 문제는 경고로 처리 (실패로 간주하지 않음)
			fi
		elif [ -f "$PROJECT_ROOT/.venv/bin/ruff" ] || [ -f "$PROJECT_ROOT/venv/bin/ruff" ]; then
			RUFF_CMD=""
			if [ -f "$PROJECT_ROOT/.venv/bin/ruff" ]; then
				RUFF_CMD="$PROJECT_ROOT/.venv/bin/ruff"
			elif [ -f "$PROJECT_ROOT/venv/bin/ruff" ]; then
				RUFF_CMD="$PROJECT_ROOT/venv/bin/ruff"
			fi
			if [ -n "$RUFF_CMD" ]; then
				echo "${BLUE}   Running ruff format (from venv)...${NC}"
				if "$RUFF_CMD" format --check "$PROJECT_ROOT" 2>&1; then
					echo "${GREEN}   ✅ ruff format check passed${NC}"
				else
					echo "${YELLOW}   ⚠️  Code formatting issues detected. Run 'ruff format' to fix.${NC}"
				fi
			fi
		fi
		
		# 2d. pre-commit run --all-files (설정되어 있는 경우)
		if [ -f "$PROJECT_ROOT/.pre-commit-config.yaml" ]; then
			if command -v pre-commit >/dev/null 2>&1; then
				echo "${BLUE}   Running pre-commit hooks...${NC}"
				if pre-commit run --all-files 2>&1; then
					echo "${GREEN}   ✅ pre-commit hooks passed${NC}"
				else
					add_error "pre-commit hooks failed"
					echo "${RED}   ❌ pre-commit hooks failed${NC}"
				fi
			elif [ -f "$PROJECT_ROOT/.venv/bin/pre-commit" ] || [ -f "$PROJECT_ROOT/venv/bin/pre-commit" ]; then
				PRE_COMMIT_CMD=""
				if [ -f "$PROJECT_ROOT/.venv/bin/pre-commit" ]; then
					PRE_COMMIT_CMD="$PROJECT_ROOT/.venv/bin/pre-commit"
				elif [ -f "$PROJECT_ROOT/venv/bin/pre-commit" ]; then
					PRE_COMMIT_CMD="$PROJECT_ROOT/venv/bin/pre-commit"
				fi
				if [ -n "$PRE_COMMIT_CMD" ]; then
					echo "${BLUE}   Running pre-commit hooks (from venv)...${NC}"
					if "$PRE_COMMIT_CMD" run --all-files 2>&1; then
						echo "${GREEN}   ✅ pre-commit hooks passed${NC}"
					else
						add_error "pre-commit hooks failed"
						echo "${RED}   ❌ pre-commit hooks failed${NC}"
					fi
				fi
			else
				echo "${YELLOW}   ⚠️  pre-commit not found. Install with: poetry add pre-commit --group quality${NC}"
			fi
		fi
		
		# 2e. pytest 실행 (tests/ 디렉토리가 있는 경우)
		if [ -d "$PROJECT_ROOT/tests" ] || [ -d "$PROJECT_ROOT/test" ]; then
			if command -v pytest >/dev/null 2>&1; then
				echo "${BLUE}   Running pytest...${NC}"
				if pytest "$PROJECT_ROOT" 2>&1; then
					echo "${GREEN}   ✅ pytest passed${NC}"
				else
					add_error "pytest failed"
					echo "${RED}   ❌ pytest failed${NC}"
				fi
			elif [ -f "$PROJECT_ROOT/.venv/bin/pytest" ] || [ -f "$PROJECT_ROOT/venv/bin/pytest" ]; then
				PYTEST_CMD=""
				if [ -f "$PROJECT_ROOT/.venv/bin/pytest" ]; then
					PYTEST_CMD="$PROJECT_ROOT/.venv/bin/pytest"
				elif [ -f "$PROJECT_ROOT/venv/bin/pytest" ]; then
					PYTEST_CMD="$PROJECT_ROOT/venv/bin/pytest"
				fi
				if [ -n "$PYTEST_CMD" ]; then
					echo "${BLUE}   Running pytest (from venv)...${NC}"
					if "$PYTEST_CMD" "$PROJECT_ROOT" 2>&1; then
						echo "${GREEN}   ✅ pytest passed${NC}"
					else
						add_error "pytest failed"
						echo "${RED}   ❌ pytest failed${NC}"
					fi
				fi
			else
				echo "${YELLOW}   ⚠️  pytest not found. Install with: poetry add pytest --group dev${NC}"
			fi
		fi
		;;
	node)
		echo "${BLUE}📦 [Node.js] Running Node.js-specific verification...${NC}"
		
		# 2a. pnpm/npm install 확인
		if [ "$DETECTED_PACKAGE_MANAGER" = "pnpm" ]; then
			if ! command -v pnpm >/dev/null 2>&1; then
				echo "${YELLOW}⚠️  pnpm not found. Install with: npm install -g pnpm${NC}"
			else
				echo "${BLUE}   Checking node_modules...${NC}"
				if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
					echo "${YELLOW}   ⚠️  node_modules not found. Run 'pnpm install' first.${NC}"
				fi
			fi
		elif [ "$DETECTED_PACKAGE_MANAGER" = "npm" ]; then
			if ! command -v npm >/dev/null 2>&1; then
				echo "${YELLOW}⚠️  npm not found in PATH${NC}"
			else
				echo "${BLUE}   Checking node_modules...${NC}"
				if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
					echo "${YELLOW}   ⚠️  node_modules not found. Run 'npm install' first.${NC}"
				fi
			fi
		fi
		
		# 2b. ESLint 실행
		if [ -f "$PROJECT_ROOT/.eslintrc.js" ] || [ -f "$PROJECT_ROOT/.eslintrc.cjs" ] || [ -f "$PROJECT_ROOT/.eslintrc.json" ] || [ -f "$PROJECT_ROOT/eslint.config.js" ]; then
			if [ "$DETECTED_PACKAGE_MANAGER" = "pnpm" ] && command -v pnpm >/dev/null 2>&1; then
				echo "${BLUE}   Running ESLint (via pnpm)...${NC}"
				if pnpm run lint 2>&1 || pnpm exec eslint . 2>&1; then
					echo "${GREEN}   ✅ ESLint passed${NC}"
				else
					add_error "ESLint failed"
					echo "${RED}   ❌ ESLint failed${NC}"
				fi
			elif [ "$DETECTED_PACKAGE_MANAGER" = "npm" ] && command -v npm >/dev/null 2>&1; then
				echo "${BLUE}   Running ESLint (via npm)...${NC}"
				if npm run lint 2>&1 || npx eslint . 2>&1; then
					echo "${GREEN}   ✅ ESLint passed${NC}"
				else
					add_error "ESLint failed"
					echo "${RED}   ❌ ESLint failed${NC}"
				fi
			fi
		fi
		
		# 2c. TypeScript 타입 체크 (tsconfig.json이 있는 경우)
		if [ -f "$PROJECT_ROOT/tsconfig.json" ]; then
			if [ "$DETECTED_PACKAGE_MANAGER" = "pnpm" ] && command -v pnpm >/dev/null 2>&1; then
				echo "${BLUE}   Running TypeScript type check (via pnpm)...${NC}"
				if pnpm run type-check 2>&1 || pnpm exec tsc --noEmit 2>&1; then
					echo "${GREEN}   ✅ TypeScript type check passed${NC}"
				else
					add_error "TypeScript type check failed"
					echo "${RED}   ❌ TypeScript type check failed${NC}"
				fi
			elif [ "$DETECTED_PACKAGE_MANAGER" = "npm" ] && command -v npm >/dev/null 2>&1; then
				echo "${BLUE}   Running TypeScript type check (via npm)...${NC}"
				if npm run type-check 2>&1 || npx tsc --noEmit 2>&1; then
					echo "${GREEN}   ✅ TypeScript type check passed${NC}"
				else
					add_error "TypeScript type check failed"
					echo "${RED}   ❌ TypeScript type check failed${NC}"
				fi
			fi
		fi
		
		# 2d. 테스트 실행
		if [ -d "$PROJECT_ROOT/tests" ] || [ -d "$PROJECT_ROOT/__tests__" ] || [ -f "$PROJECT_ROOT/package.json" ]; then
			if [ "$DETECTED_PACKAGE_MANAGER" = "pnpm" ] && command -v pnpm >/dev/null 2>&1; then
				echo "${BLUE}   Running tests (via pnpm)...${NC}"
				if pnpm run test 2>&1 || pnpm test 2>&1; then
					echo "${GREEN}   ✅ Tests passed${NC}"
				else
					add_error "Tests failed"
					echo "${RED}   ❌ Tests failed${NC}"
				fi
			elif [ "$DETECTED_PACKAGE_MANAGER" = "npm" ] && command -v npm >/dev/null 2>&1; then
				echo "${BLUE}   Running tests (via npm)...${NC}"
				if npm run test 2>&1 || npm test 2>&1; then
					echo "${GREEN}   ✅ Tests passed${NC}"
				else
					add_error "Tests failed"
					echo "${RED}   ❌ Tests failed${NC}"
				fi
			fi
		fi
		;;
	go)
		echo "${BLUE}🔷 [Go] Running Go-specific verification...${NC}"
		
		if command -v go >/dev/null 2>&1; then
			echo "${BLUE}   Running go fmt...${NC}"
			if go fmt ./... 2>&1; then
				echo "${GREEN}   ✅ go fmt passed${NC}"
			else
				add_error "go fmt failed"
				echo "${RED}   ❌ go fmt failed${NC}"
			fi
			
			echo "${BLUE}   Running go vet...${NC}"
			if go vet ./... 2>&1; then
				echo "${GREEN}   ✅ go vet passed${NC}"
			else
				add_error "go vet failed"
				echo "${RED}   ❌ go vet failed${NC}"
			fi
			
			if [ -d "$PROJECT_ROOT" ]; then
				echo "${BLUE}   Running go test...${NC}"
				if go test ./... 2>&1; then
					echo "${GREEN}   ✅ go test passed${NC}"
				else
					add_error "go test failed"
					echo "${RED}   ❌ go test failed${NC}"
				fi
			fi
		else
			echo "${YELLOW}⚠️  go not found in PATH${NC}"
		fi
		;;
	rust)
		echo "${BLUE}🦀 [Rust] Running Rust-specific verification...${NC}"
		
		if command -v cargo >/dev/null 2>&1; then
			echo "${BLUE}   Running cargo fmt --check...${NC}"
			if cargo fmt --check 2>&1; then
				echo "${GREEN}   ✅ cargo fmt passed${NC}"
			else
				echo "${YELLOW}   ⚠️  Code formatting issues detected. Run 'cargo fmt' to fix.${NC}"
			fi
			
			echo "${BLUE}   Running cargo clippy...${NC}"
			if cargo clippy 2>&1; then
				echo "${GREEN}   ✅ cargo clippy passed${NC}"
			else
				add_error "cargo clippy failed"
				echo "${RED}   ❌ cargo clippy failed${NC}"
			fi
			
			echo "${BLUE}   Running cargo test...${NC}"
			if cargo test 2>&1; then
				echo "${GREEN}   ✅ cargo test passed${NC}"
			else
				add_error "cargo test failed"
				echo "${RED}   ❌ cargo test failed${NC}"
			fi
		else
			echo "${YELLOW}⚠️  cargo not found in PATH${NC}"
		fi
		;;
	*)
		echo "${RED}❌ Error: Unsupported stack: $DETECTED_STACK${NC}"
		exit 1
		;;
esac

# 3. 인프라 체크 (kubefwd가 필요한 서비스 접근성 확인)
echo "${BLUE}🏗️  [Infrastructure] Checking infrastructure access...${NC}"

# kubefwd가 필요한 서비스 목록 (예시)
KUBEFWD_SERVICES="aiops chatops"

if command -v kubectl >/dev/null 2>&1; then
	# Kubernetes 클러스터 접근 확인
	if kubectl cluster-info >/dev/null 2>&1; then
		echo "${GREEN}   ✅ Kubernetes cluster accessible${NC}"
	else
		echo "${YELLOW}   ⚠️  Kubernetes cluster not accessible${NC}"
		echo "${YELLOW}   💡 Tip: Run 'mise run infra:up' to start kubefwd for local services${NC}"
	fi
elif command -v kubefwd >/dev/null 2>&1; then
	echo "${YELLOW}   ⚠️  kubectl not found, but kubefwd is available${NC}"
	echo "${YELLOW}   💡 Tip: Run 'mise run infra:up' to start kubefwd for local services${NC}"
else
	echo "${YELLOW}   ⚠️  kubectl/kubefwd not found. Infrastructure checks skipped.${NC}"
fi

# 4. 검증 결과 종합
echo ""
echo "${BLUE}📊 [Auto Verify] Verification Summary:${NC}"

if [ "$VERIFICATION_FAILED" -eq 0 ]; then
	echo "${GREEN}✅ All verifications passed successfully!${NC}"
	exit 0
else
	echo "${RED}❌ Verification failed with the following errors:${NC}"
	echo "$VERIFICATION_ERRORS"
	exit 1
fi

