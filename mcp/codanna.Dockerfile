# Codanna MCP Server
# Rust 기반의 시맨틱 코드 검색 및 분석 도구
#
# 빌드: docker build -f codanna.Dockerfile -t mcp-codanna .
# 실행: docker run --rm -it -v /path/to/project:/workspace mcp-codanna
#
# 주의: Rust 빌드로 인해 초기 빌드에 5-10분 소요될 수 있습니다.
# Codanna는 Rust 2024 edition을 사용하여 nightly toolchain이 필요합니다.

# ====================
# Builder Stage
# ====================
FROM rust:slim-bookworm AS builder

# 빌드 의존성 설치 (make, gcc 등 포함)
RUN apt-get update && apt-get install -y \
  pkg-config \
  libssl-dev \
  git \
  ca-certificates \
  curl \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# 사내 SSL 인증서 추가 (SKCC_ROOT.pem)
COPY SKCC_ROOT.pem /usr/local/share/ca-certificates/SKCC_ROOT.crt
RUN update-ca-certificates

# Rust nightly 설치 (edition2024 지원)
RUN rustup default nightly && rustup update nightly

# Git을 통해 crates.io를 우회하여 직접 소스에서 빌드
ENV CARGO_NET_GIT_FETCH_WITH_CLI=true

# Codanna를 GitHub에서 직접 설치
RUN cargo install --git https://github.com/bartolli/codanna.git --all-features

# ====================
# Runtime Stage
# ====================
FROM debian:bookworm-slim

# 런타임 의존성 (SSL 인증서 등)
RUN apt-get update && apt-get install -y \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# 빌더에서 바이너리 복사
COPY --from=builder /usr/local/cargo/bin/codanna /usr/local/bin/codanna

# 작업 디렉터리
WORKDIR /workspace

# 엔트리포인트 - watch 모드로 파일 변경 감지
ENTRYPOINT ["codanna", "serve"]
CMD ["--watch"]
