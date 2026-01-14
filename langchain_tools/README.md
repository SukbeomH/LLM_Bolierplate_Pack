# LangChain Tools

LangChain 1.0 기반 검증 도구 및 미들웨어 패키지.

## 설치

```bash
uv add langchain-tools
# 또는 개발 모드
uv pip install -e .
```

## 환경 변수

```bash
# LLM 제공자 설정 (openai, anthropic, google)
export LANGCHAIN_PROVIDER=openai
export LANGCHAIN_MODEL_NAME=gpt-4o

# 또는 전체 모델 문자열
export LANGCHAIN_MODEL=anthropic:claude-3-5-sonnet-20241022
```

## 사용법

### 개별 도구 사용

```python
from langchain_tools.tools import SimplifierTool, SecurityAuditTool

# 코드 복잡도 분석
simplifier = SimplifierTool()
result = simplifier.invoke({"target_path": "src/"})
print(result)

# 보안 감사
audit = SecurityAuditTool()
result = audit.invoke({})
print(result)
```

### 통합 에이전트 사용

```python
from langchain_tools import create_verification_agent

# 환경 변수로 모델 설정
agent = create_verification_agent()

# 직접 모델 지정
agent = create_verification_agent("google:gemini-2.0-flash")

# Human-in-the-loop 활성화
agent = create_verification_agent(use_human_in_the_loop=True)

# 에이전트 실행
result = await agent.invoke({
    "messages": [{"role": "user", "content": "코드 품질 검증을 실행해주세요"}]
})
```

## 포함된 도구

| 도구 | 설명 |
|------|------|
| `StackDetectorTool` | 프로젝트 스택 감지 (Python/Node/Go/Rust) |
| `AutoVerifyTool` | 스택별 자동 검증 (lint, format, test) |
| `SimplifierTool` | 코드 복잡도 분석 및 단순화 제안 |
| `SecurityAuditTool` | 보안 감사 (safety check, npm audit) |
| `LogAnalyzerTool` | 로그 파일 분석, ERROR/CRITICAL 감지 |
| `GitGuardTool` | Git 규칙 준수 검증 |
| `VisualVerifierTool` | 웹 프로젝트 시각적 검증 가이드 |
| `ClaudeKnowledgeUpdaterTool` | CLAUDE.md 지식 업데이트 |

## 미들웨어

- `VerifyFeedbackLoopMiddleware`: Plan → Build → Verify → Approve 피드백 루프

LangChain 네이티브 미들웨어와 함께 사용:
- `TodoListMiddleware`: 작업 추적
- `ToolRetryMiddleware`: 도구 재시도
- `HumanInTheLoopMiddleware`: Human-in-the-loop 승인
