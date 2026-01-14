#!/bin/sh
# setup_infra.sh - 인프라 설정 자동화
#
# 목적: kubefwd 기반의 로컬 인프라 접근성을 체크하고,
# 사내망 자격 증명 및 인증서(certifi) 설치 여부를 확인합니다.
#
# 사용법:
#   scripts/core/setup_infra.sh
#   또는
#   mise run infra:setup
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

echo "${BLUE}🔧 [Infrastructure Setup] Starting infrastructure setup check...${NC}"

# 1. kubefwd 설치 여부 확인
echo "${BLUE}1. Checking kubefwd installation...${NC}"
if command -v kubefwd >/dev/null 2>&1; then
	echo "${GREEN}   ✅ kubefwd is installed${NC}"
	KUBEFWD_VERSION=$(kubefwd version 2>/dev/null || echo "unknown")
	echo "   Version: $KUBEFWD_VERSION"
else
	echo "${YELLOW}   ⚠️  kubefwd is not installed${NC}"
	echo "${YELLOW}   Install with: brew install txn2/tap/kubefwd (macOS)${NC}"
	echo "${YELLOW}   Or visit: https://github.com/txn2/kubefwd${NC}"
fi

# 2. kubectl 설치 여부 확인
echo "${BLUE}2. Checking kubectl installation...${NC}"
if command -v kubectl >/dev/null 2>&1; then
	echo "${GREEN}   ✅ kubectl is installed${NC}"
	KUBECTL_VERSION=$(kubectl version --client --short 2>/dev/null | head -1 || echo "unknown")
	echo "   $KUBECTL_VERSION"
else
	echo "${YELLOW}   ⚠️  kubectl is not installed${NC}"
	echo "${YELLOW}   Install with: brew install kubectl (macOS)${NC}"
	echo "${YELLOW}   Or visit: https://kubernetes.io/docs/tasks/tools/${NC}"
fi

# 3. Kubernetes 클러스터 접근성 확인
echo "${BLUE}3. Checking Kubernetes cluster access...${NC}"
if command -v kubectl >/dev/null 2>&1; then
	if kubectl cluster-info >/dev/null 2>&1; then
		echo "${GREEN}   ✅ Kubernetes cluster is accessible${NC}"
		CLUSTER_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "unknown")
		echo "   Context: $CLUSTER_CONTEXT"
	else
		echo "${YELLOW}   ⚠️  Kubernetes cluster is not accessible${NC}"
		echo "${YELLOW}   Please configure kubectl context or check your credentials${NC}"
	fi
else
	echo "${YELLOW}   ⚠️  kubectl not found, skipping cluster check${NC}"
fi

# 4. Python 프로젝트인 경우 certifi 패키지 확인
echo "${BLUE}4. Checking Python certificate setup...${NC}"
if [ -f "$PROJECT_ROOT/pyproject.toml" ] || [ -f "$PROJECT_ROOT/requirements.txt" ]; then
	if command -v uv >/dev/null 2>&1 && [ -f "$PROJECT_ROOT/uv.lock" ]; then
		# uv 프로젝트인 경우
		if grep -q "certifi" "$PROJECT_ROOT/pyproject.toml" 2>/dev/null || grep -q "certifi" "$PROJECT_ROOT/uv.lock" 2>/dev/null; then
			echo "${GREEN}   ✅ certifi package is installed${NC}"
		else
			echo "${YELLOW}   ⚠️  certifi package not found${NC}"
			echo "${YELLOW}   Install with: uv add certifi --dev${NC}"
			echo "${YELLOW}   This is required for self-signed certificate support in internal networks${NC}"
		fi
	elif command -v poetry >/dev/null 2>&1 && [ -f "$PROJECT_ROOT/poetry.lock" ]; then
		# Poetry 프로젝트인 경우 (마이그레이션 전)
		if grep -q "certifi" "$PROJECT_ROOT/pyproject.toml" 2>/dev/null || grep -q "certifi" "$PROJECT_ROOT/poetry.lock" 2>/dev/null; then
			echo "${GREEN}   ✅ certifi package is installed${NC}"
		else
			echo "${YELLOW}   ⚠️  certifi package not found${NC}"
			echo "${YELLOW}   Install with: poetry add certifi --group dev${NC}"
			echo "${YELLOW}   Or migrate to uv: scripts/core/migrate_to_uv.sh${NC}"
			echo "${YELLOW}   This is required for self-signed certificate support in internal networks${NC}"
		fi
	elif [ -f "$PROJECT_ROOT/requirements.txt" ]; then
		# requirements.txt 기반 프로젝트인 경우
		if grep -q "^certifi" "$PROJECT_ROOT/requirements.txt" 2>/dev/null; then
			echo "${GREEN}   ✅ certifi package is listed in requirements.txt${NC}"
		else
			echo "${YELLOW}   ⚠️  certifi package not found in requirements.txt${NC}"
			echo "${YELLOW}   Add: certifi to requirements.txt${NC}"
		fi
	fi
else
	echo "${BLUE}   ℹ️  Not a Python project, skipping certifi check${NC}"
fi

# 5. kubefwd 사용 가이드 출력
echo "${BLUE}5. kubefwd usage guide...${NC}"
if command -v kubefwd >/dev/null 2>&1 && command -v kubectl >/dev/null 2>&1; then
	echo "${GREEN}   ✅ kubefwd is ready to use${NC}"
	echo ""
	echo "${BLUE}   Usage examples:${NC}"
	echo "   # Forward all services in a namespace:"
	echo "   sudo kubefwd svc -n <namespace>"
	echo ""
	echo "   # Forward specific services:"
	echo "   sudo kubefwd svc -n <namespace> -s <service-name>"
	echo ""
	echo "${YELLOW}   Note: kubefwd requires sudo privileges${NC}"
	echo "${YELLOW}   Make sure you have proper Kubernetes credentials configured${NC}"
else
	echo "${YELLOW}   ⚠️  kubefwd is not ready. Please install kubefwd and kubectl first${NC}"
fi

# 6. 사내망 인증서 설치 안내 (Python 프로젝트인 경우)
if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
	echo ""
	echo "${BLUE}6. Internal network certificate setup (Python)...${NC}"
	echo "${BLUE}   For self-signed certificate support:${NC}"
	if command -v uv >/dev/null 2>&1 && [ -f "$PROJECT_ROOT/uv.lock" ]; then
		echo "   1. Install certifi: uv add certifi --dev"
		echo "   2. Configure your application to use certifi certificates"
		echo "   3. See: .cursor/docs/raw/PythonEnvDocs/Python/가상 환경에 Self-Signed Certificate 추가"
	elif command -v poetry >/dev/null 2>&1 && [ -f "$PROJECT_ROOT/poetry.lock" ]; then
		echo "   1. Install certifi: poetry add certifi --group dev"
		echo "   2. Or migrate to uv: scripts/core/migrate_to_uv.sh"
		echo "   3. Configure your application to use certifi certificates"
		echo "   4. See: .cursor/docs/raw/PythonEnvDocs/Python/가상 환경에 Self-Signed Certificate 추가"
	fi
fi

echo ""
echo "${GREEN}✅ Infrastructure setup check completed${NC}"

