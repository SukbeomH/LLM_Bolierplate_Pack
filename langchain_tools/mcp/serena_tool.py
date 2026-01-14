"""Serena MCP Tool.

Docker로 실행되는 Serena MCP를 LangChain Tool로 래핑.
심볼 기반 코드 검색 및 편집.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool
from langchain_tools.mcp.docker_client import MCPDockerClient


class SerenaMCPInput(BaseModel):
    """SerenaMCPTool 입력 스키마."""

    action: str = Field(
        description="수행할 액션: 'search_symbol', 'find_references', 'edit_symbol'",
    )
    symbol: str = Field(
        description="검색하거나 편집할 심볼 이름",
    )
    query: str | None = Field(
        default=None,
        description="검색 쿼리 (search_symbol에 사용)",
    )
    new_content: str | None = Field(
        default=None,
        description="새 내용 (edit_symbol에 사용)",
    )


class SerenaMCPTool(BoilerplateBaseTool):
    """Serena MCP를 LangChain Tool로 래핑.

    Docker 컨테이너로 실행되는 Serena MCP와 JSON-RPC 통신.
    심볼 기반 코드 검색 및 정밀 편집을 제공합니다.
    """

    name: str = "serena_mcp"
    description: str = "심볼 기반 코드 검색 및 편집. Docker MCP 서버 통신."
    args_schema: type[BaseModel] = SerenaMCPInput

    def _run(
        self,
        action: str,
        symbol: str,
        query: str | None = None,
        new_content: str | None = None,
    ) -> dict[str, Any]:
        """Serena MCP 도구를 실행합니다."""
        client = MCPDockerClient("serena", project_path=self.project_root)

        tool_map = {
            "search_symbol": "search_symbol",
            "find_references": "find_references",
            "edit_symbol": "edit_symbol",
        }

        if action not in tool_map:
            return {
                "status": "error",
                "message": f"Unknown action: {action}. Available: {list(tool_map.keys())}",
            }

        arguments: dict[str, Any] = {"symbol": symbol}
        if query:
            arguments["query"] = query
        if new_content:
            arguments["new_content"] = new_content

        result = client.call_tool(tool_map[action], arguments)
        return result

    async def _arun(
        self,
        action: str,
        symbol: str,
        query: str | None = None,
        new_content: str | None = None,
    ) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(action, symbol, query, new_content)
