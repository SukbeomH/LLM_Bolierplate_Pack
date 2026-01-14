# Shrimp Task Manager MCP Server
# Node.js 기반의 구조화된 작업 관리 도구
#
# 빌드: docker build -f shrimp.Dockerfile -t mcp-shrimp .
# 실행: docker run --rm -it -v /path/to/project:/workspace -v shrimp-data:/data mcp-shrimp

FROM node:20-slim

# 시스템 의존성
RUN apt-get update && apt-get install -y \
  git \
  && rm -rf /var/lib/apt/lists/*

# 앱 디렉터리
WORKDIR /app

# Shrimp Task Manager 클론 및 빌드
RUN git clone --depth 1 https://github.com/cjo4m06/mcp-shrimp-task-manager.git . && \
  npm ci --only=production=false && \
  npm run build && \
  npm prune --production

# 데이터 디렉터리 생성
RUN mkdir -p /data

# 환경 변수 기본값
ENV DATA_DIR=/data
ENV TEMPLATES_USE=ko
ENV ENABLE_GUI=false
ENV NODE_ENV=production

# 작업 디렉터리 (프로젝트 마운트용)
WORKDIR /workspace

# 엔트리포인트
ENTRYPOINT ["node", "/app/dist/index.js"]
