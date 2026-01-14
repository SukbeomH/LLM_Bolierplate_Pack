"""LangChain Tools 설정 모듈.

환경 변수를 통한 설정 관리를 제공합니다.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class LangChainToolsConfig:
    """LangChain Tools 전역 설정.

    환경 변수:
        LANGCHAIN_MODEL: 전체 모델 문자열 (예: "openai:gpt-4o")
        LANGCHAIN_PROVIDER: LLM 제공자 (openai, anthropic, google)
        LANGCHAIN_MODEL_NAME: 모델 이름
        LANGCHAIN_TOOLS_LOG_LEVEL: 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
        LANGCHAIN_TOOLS_TIMEOUT: 도구 실행 타임아웃 (초)
    """

    # LLM 설정
    provider: Literal["openai", "anthropic", "google"] = field(
        default_factory=lambda: os.getenv("LANGCHAIN_PROVIDER", "openai")  # type: ignore
    )
    model_name: str | None = field(
        default_factory=lambda: os.getenv("LANGCHAIN_MODEL_NAME")
    )
    full_model: str | None = field(
        default_factory=lambda: os.getenv("LANGCHAIN_MODEL")
    )

    # 도구 설정
    log_level: str = field(
        default_factory=lambda: os.getenv("LANGCHAIN_TOOLS_LOG_LEVEL", "INFO")
    )
    timeout: int = field(
        default_factory=lambda: int(os.getenv("LANGCHAIN_TOOLS_TIMEOUT", "120"))
    )

    # 검증 설정
    max_tool_retries: int = field(
        default_factory=lambda: int(os.getenv("LANGCHAIN_TOOLS_MAX_RETRIES", "2"))
    )

    def get_model_string(self) -> str:
        """설정된 모델 문자열을 반환합니다."""
        if self.full_model:
            return self.full_model

        if self.model_name:
            return f"{self.provider}:{self.model_name}"

        # 제공자별 기본 모델
        default_models = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "google": "gemini-2.0-flash",
        }

        return f"{self.provider}:{default_models.get(self.provider, 'gpt-4o')}"


# 전역 설정 인스턴스
config = LangChainToolsConfig()
