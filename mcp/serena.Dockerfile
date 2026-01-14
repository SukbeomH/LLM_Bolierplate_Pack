# Serena MCP Server
# Python/uv 기반의 심볼 기반 코드 검색 및 편집 도구
#
# 빌드: docker build -f serena.Dockerfile -t mcp-serena .
# 실행: docker run --rm -it -v /path/to/project:/workspace mcp-serena

FROM python:3.12-slim

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# uv 설치 (공식 설치 스크립트 사용)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# 작업 디렉터리
WORKDIR /workspace

# Serena 사전 캐싱 (첫 실행 속도 향상)
RUN uvx --from git+https://github.com/oraios/serena serena --help 2>/dev/null || true

# 엔트리포인트 - stdio 통신을 위해 직접 실행
ENTRYPOINT ["uvx", "--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"]
CMD ["--context", "ide-assistant", "--mode", "interactive"]
