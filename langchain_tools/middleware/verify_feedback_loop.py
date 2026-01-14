"""검증 피드백 루프 미들웨어.

LangChain 네이티브 미들웨어를 활용하여 통합 검증 피드백 루프를 구현합니다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from langchain.agents.middleware import (
    AgentMiddleware,
    before_agent,
    after_agent,
    wrap_tool_call,
)
from pydantic import BaseModel


@dataclass
class VerifyFeedbackLoopState:
    """피드백 루프 상태."""

    plan_status: str = "pending"
    build_status: str = "pending"
    verify_results: dict[str, Any] = field(default_factory=dict)
    approve_status: str = "pending"
    errors: list[str] = field(default_factory=list)


class VerifyFeedbackLoopMiddleware(AgentMiddleware):
    """통합 검증 피드백 루프 미들웨어.

    Plan -> Build -> Verify -> Approve 단계를 추적하고
    검증 결과를 수집합니다.

    LangChain의 TodoListMiddleware, ToolRetryMiddleware,
    HumanInTheLoopMiddleware와 함께 사용하면 효과적입니다.
    """

    def __init__(
        self,
        *,
        auto_verify_on_complete: bool = True,
        require_approval: bool = True,
    ):
        """미들웨어 초기화.

        Args:
            auto_verify_on_complete: 빌드 완료 후 자동 검증 실행
            require_approval: 적용 전 승인 요구
        """
        self.auto_verify = auto_verify_on_complete
        self.require_approval = require_approval
        self._states: dict[str, VerifyFeedbackLoopState] = {}

    def get_state(self, session_id: str = "default") -> VerifyFeedbackLoopState:
        """세션의 상태를 반환합니다."""
        if session_id not in self._states:
            self._states[session_id] = VerifyFeedbackLoopState()
        return self._states[session_id]

    def update_plan_status(
        self,
        status: str,
        session_id: str = "default",
    ) -> None:
        """Plan 단계 상태 업데이트."""
        state = self.get_state(session_id)
        state.plan_status = status

    def update_build_status(
        self,
        status: str,
        session_id: str = "default",
    ) -> None:
        """Build 단계 상태 업데이트."""
        state = self.get_state(session_id)
        state.build_status = status

    def add_verify_result(
        self,
        tool_name: str,
        result: dict[str, Any],
        session_id: str = "default",
    ) -> None:
        """검증 결과 추가."""
        state = self.get_state(session_id)
        state.verify_results[tool_name] = result

    def update_approve_status(
        self,
        status: str,
        session_id: str = "default",
    ) -> None:
        """Approve 단계 상태 업데이트."""
        state = self.get_state(session_id)
        state.approve_status = status

    def get_summary(self, session_id: str = "default") -> dict[str, Any]:
        """현재 상태 요약을 반환합니다."""
        state = self.get_state(session_id)

        # 전체 상태 결정
        has_errors = any(
            r.get("status") == "failed"
            for r in state.verify_results.values()
        )

        overall_status = "passed"
        if state.approve_status == "rejected":
            overall_status = "rejected"
        elif has_errors:
            overall_status = "failed"
        elif state.approve_status == "approved":
            overall_status = "approved"
        elif state.verify_results:
            overall_status = "pending_approval"

        return {
            "overall_status": overall_status,
            "steps": {
                "plan": {"status": state.plan_status},
                "build": {"status": state.build_status},
                "verify": state.verify_results,
                "approve": {"status": state.approve_status},
            },
            "errors": state.errors,
        }

    def reset(self, session_id: str = "default") -> None:
        """상태 초기화."""
        if session_id in self._states:
            del self._states[session_id]


# 편의 함수: 미들웨어 데코레이터로 사용
def create_verify_feedback_loop_hooks(
    middleware: VerifyFeedbackLoopMiddleware,
    session_id: str = "default",
) -> list[Callable[..., Any]]:
    """검증 피드백 루프 훅을 생성합니다.

    사용 예:
        middleware = VerifyFeedbackLoopMiddleware()
        hooks = create_verify_feedback_loop_hooks(middleware)
        agent = create_agent(model, tools=tools, middleware=hooks)
    """

    @before_agent
    async def init_feedback_loop(state: dict[str, Any]) -> dict[str, Any]:
        """에이전트 시작 전 피드백 루프 초기화."""
        middleware.reset(session_id)
        middleware.update_plan_status("in_progress", session_id)
        return state

    @wrap_tool_call
    async def track_tool_calls(
        tool_name: str,
        tool_input: dict[str, Any],
        call_next: Callable[..., Any],
    ) -> Any:
        """도구 호출 추적."""
        result = await call_next(tool_name, tool_input)

        # 검증 도구 결과 추적
        verify_tools = [
            "auto_verify",
            "simplifier",
            "security_audit",
            "log_analyzer",
            "git_guard",
            "visual_verifier",
        ]

        if tool_name in verify_tools and isinstance(result, dict):
            middleware.add_verify_result(tool_name, result, session_id)

        return result

    @after_agent
    async def finalize_feedback_loop(state: dict[str, Any]) -> dict[str, Any]:
        """에이전트 종료 후 피드백 루프 완료."""
        summary = middleware.get_summary(session_id)
        state["verify_feedback_loop"] = summary
        return state

    return [init_feedback_loop, track_tool_calls, finalize_feedback_loop]
