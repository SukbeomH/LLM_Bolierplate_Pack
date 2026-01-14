"""검증 에이전트 구성.

LangChain 1.0의 create_agent를 사용하여 통합 검증 에이전트를 생성합니다.
LLM 모델은 환경 변수 또는 설정으로 변경 가능합니다.

지원 미들웨어 (LangChain 1.0 built-in):
- TodoListMiddleware: 복잡한 다단계 작업 관리
- ToolRetryMiddleware: 도구 실패 시 자동 재시도
- HumanInTheLoopMiddleware: 중요 작업 사람 승인
- PIIMiddleware: 이메일, 신용카드, API 키 등 민감 정보 필터링
- LLMToolSelectorMiddleware: 도구가 많을 때 관련 도구만 선택
- ModelFallbackMiddleware: 모델 장애 시 대체 모델로 폴백
"""

from __future__ import annotations

import os
from typing import Any

from langchain.agents import create_agent
from langchain.agents.middleware import (
    HumanInTheLoopMiddleware,
    LLMToolSelectorMiddleware,
    ModelFallbackMiddleware,
    PIIMiddleware,
    TodoListMiddleware,
    ToolRetryMiddleware,
)
from langchain.tools import BaseTool

from langchain_tools.tools import (
    AutoVerifyTool,
    ClaudeKnowledgeUpdaterTool,
    GitGuardTool,
    LogAnalyzerTool,
    SecurityAuditTool,
    SimplifierTool,
    StackDetectorTool,
    VisualVerifierTool,
)
from langchain_tools.middleware import VerifyFeedbackLoopMiddleware


def get_model_string() -> str:
    """환경 변수에서 모델 문자열을 가져옵니다.

    환경 변수:
        LANGCHAIN_MODEL: 전체 모델 문자열 (예: "openai:gpt-4o")
        LANGCHAIN_PROVIDER: 제공자 (openai, anthropic, google)
        LANGCHAIN_MODEL_NAME: 모델 이름 (gpt-4o, claude-3-5-sonnet-20241022, gemini-2.0-flash)

    우선순위: LANGCHAIN_MODEL > LANGCHAIN_PROVIDER + LANGCHAIN_MODEL_NAME > 기본값
    """
    # 전체 모델 문자열 우선
    full_model = os.getenv("LANGCHAIN_MODEL")
    if full_model:
        return full_model

    # 제공자 + 모델 이름
    provider = os.getenv("LANGCHAIN_PROVIDER", "openai")
    model_name = os.getenv("LANGCHAIN_MODEL_NAME")

    if model_name:
        return f"{provider}:{model_name}"

    # 제공자별 기본 모델
    default_models = {
        "openai": "gpt-4o",
        "anthropic": "claude-3-5-sonnet-20241022",
        "google": "gemini-2.0-flash",
    }

    return f"{provider}:{default_models.get(provider, 'gpt-4o')}"


def get_all_tools() -> list[BaseTool]:
    """모든 검증 도구를 반환합니다."""
    return [
        StackDetectorTool(),
        AutoVerifyTool(),
        SimplifierTool(),
        SecurityAuditTool(),
        LogAnalyzerTool(),
        GitGuardTool(),
        VisualVerifierTool(),
        ClaudeKnowledgeUpdaterTool(),
    ]


def create_verification_agent(
    model: str | None = None,
    *,
    use_todo_list: bool = True,
    use_tool_retry: bool = True,
    use_human_in_the_loop: bool = False,
    use_pii_filter: bool = True,
    use_tool_selector: bool = False,
    use_model_fallback: bool = True,
    max_retries: int = 2,
    fallback_models: list[str] | None = None,
    tools: list[BaseTool] | None = None,
    **kwargs: Any,
) -> Any:
    """통합 검증 에이전트를 생성합니다.

    Args:
        model: LLM 모델 문자열 (예: "openai:gpt-4o").
               None이면 환경 변수에서 읽음.
        use_todo_list: TodoListMiddleware 사용 여부
        use_tool_retry: ToolRetryMiddleware 사용 여부
        use_human_in_the_loop: HumanInTheLoopMiddleware 사용 여부
        use_pii_filter: PIIMiddleware 사용 (API 키, 이메일 필터링)
        use_tool_selector: LLMToolSelectorMiddleware 사용 (도구 10개 이상 권장)
        use_model_fallback: ModelFallbackMiddleware 사용 (모델 장애 대비)
        max_retries: 도구 재시도 횟수
        fallback_models: 폴백 모델 목록 (기본: ["openai:gpt-4o-mini"])
        tools: 사용할 도구 목록. None이면 모든 검증 도구 사용.
        **kwargs: create_agent에 전달할 추가 인자

    Returns:
        구성된 LangChain 에이전트

    환경 변수:
        LANGCHAIN_MODEL: 전체 모델 문자열
        LANGCHAIN_PROVIDER: LLM 제공자 (openai, anthropic, google)
        LANGCHAIN_MODEL_NAME: 모델 이름

    Example:
        >>> # 기본 에이전트 (PII 필터, 폴백, 재시도 활성화)
        >>> agent = create_verification_agent()

        >>> # 직접 모델 지정
        >>> agent = create_verification_agent("google:gemini-2.0-flash")

        >>> # 모든 미들웨어 활성화
        >>> agent = create_verification_agent(
        ...     use_human_in_the_loop=True,
        ...     use_tool_selector=True,
        ... )
    """
    # 모델 결정
    if model is None:
        model = get_model_string()

    # 도구 목록
    if tools is None:
        tools = get_all_tools()

    # 미들웨어 구성
    middleware: list[Any] = []

    # 1. PII 필터링 (민감 정보 보호)
    if use_pii_filter:
        # API 키 패턴 차단
        middleware.append(PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32,}",
            strategy="redact",
            apply_to_input=True,
            apply_to_output=True,
        ))
        # 이메일 마스킹
        middleware.append(PIIMiddleware(
            "email",
            strategy="mask",
            apply_to_output=True,
        ))

    # 2. ToDo 리스트 (다단계 작업 관리)
    if use_todo_list:
        middleware.append(TodoListMiddleware())

    # 3. 도구 재시도 (외부 API 안정성)
    if use_tool_retry:
        middleware.append(ToolRetryMiddleware(
            max_retries=max_retries,
            backoff_factor=2.0,
            initial_delay=1.0,
        ))

    # 4. 도구 선택기 (도구 10개 이상일 때 유용)
    if use_tool_selector and len(tools) >= 10:
        middleware.append(LLMToolSelectorMiddleware(
            model="openai:gpt-4o-mini",
            max_tools=5,
        ))

    # 5. 모델 폴백 (장애 대비)
    if use_model_fallback:
        fallbacks = fallback_models or ["openai:gpt-4o-mini"]
        middleware.append(ModelFallbackMiddleware(fallback_models=fallbacks))

    # 6. Human-in-the-loop (중요 작업 승인)
    if use_human_in_the_loop:
        middleware.append(HumanInTheLoopMiddleware())

    # 7. 피드백 루프 미들웨어 (Plan-Build-Verify-Approve)
    feedback_loop = VerifyFeedbackLoopMiddleware()
    middleware.append(feedback_loop)

    return create_agent(
        model,
        tools=tools,
        middleware=middleware,
        **kwargs,
    )
