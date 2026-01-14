"""Shrimp MCP Tool.

Docker로 실행되는 Shrimp MCP를 LangChain Tool로 래핑.
구조화된 작업 관리.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool
from langchain_tools.mcp.docker_client import MCPDockerClient


class ShrimpMCPInput(BaseModel):
    """ShrimpMCPTool 입력 스키마."""

    action: str = Field(
        description="수행할 액션: 'create_task', 'list_tasks', 'update_task', 'complete_task'",
    )
    title: str | None = Field(
        default=None,
        description="작업 제목 (create_task, update_task에 사용)",
    )
    description: str | None = Field(
        default=None,
        description="작업 설명 (create_task, update_task에 사용)",
    )
    task_id: str | None = Field(
        default=None,
        description="작업 ID (update_task, complete_task에 사용)",
    )


class ShrimpMCPTool(BoilerplateBaseTool):
    """Shrimp MCP를 LangChain Tool로 래핑.

    Docker 컨테이너로 실행되는 Shrimp MCP와 JSON-RPC 통신.
    구조화된 작업 관리를 제공합니다.
    """

    name: str = "shrimp_mcp"
    description: str = "구조화된 작업 관리. Docker MCP 서버 통신."
    args_schema: type[BaseModel] = ShrimpMCPInput

    def _run(
        self,
        action: str,
        title: str | None = None,
        description: str | None = None,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """Shrimp MCP 도구를 실행합니다."""
        client = MCPDockerClient("shrimp", project_path=self.project_root)

        tool_map = {
            "create_task": "create_task",
            "list_tasks": "list_tasks",
            "update_task": "update_task",
            "complete_task": "complete_task",
        }

        if action not in tool_map:
            return {
                "status": "error",
                "message": f"Unknown action: {action}. Available: {list(tool_map.keys())}",
            }

        arguments: dict[str, Any] = {}
        if title:
            arguments["title"] = title
        if description:
            arguments["description"] = description
        if task_id:
            arguments["task_id"] = task_id

        result = client.call_tool(tool_map[action], arguments)
        return result

    async def _arun(
        self,
        action: str,
        title: str | None = None,
        description: str | None = None,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(action, title, description, task_id)
