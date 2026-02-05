---
description: Complete initial project setup -- deps verification, directory setup, codebase analysis, and memory initialization. Use when setting up a new project or after cloning.
model: sonnet
tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# Bootstrap Agent

프로젝트 초기 설정을 단일 패스로 완료한다.

## 탑재 Skills

- `bootstrap` — 핵심 부트스트랩 로직 (시스템 검증, 환경 설정, 메모리 디렉토리 검증, 코드베이스 분석)
- `codebase-mapper` — 코드베이스 구조 분석 및 문서 생성

## 오케스트레이션

1. `bootstrap` skill로 시스템 전제조건 검증 (uv, git)
2. Python 환경 설정 + 의존성 설치
3. 메모리 디렉토리 검증 (.gsd/memories/)
4. `codebase-mapper` skill로 아키텍처 문서 생성
5. 부트스트랩 상태를 파일 기반 메모리에 저장

## 제약

- 모든 단계의 성공/실패를 경험적으로 검증
- 실패 시 구체적 에러 메시지와 해결 방법 제시
- `.env` 파일 등 시크릿은 읽지 않음
