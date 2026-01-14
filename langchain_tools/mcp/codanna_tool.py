"""Codanna MCP Tool.

Docker로 실행되는 Codanna MCP를 LangChain Tool로 래핑.
시맨틱 코드 검색 및 분석.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool
from langchain_tools.mcp.docker_client import MCPDockerClient


class CodannaMCPInput(BaseModel):
    """CodannaMCPTool 입력 스키마."""

    query: str = Field(
        description="시맨틱 검색 쿼리",
    )
    max_results: int = Field(
        default=10,
        description="최대 결과 수",
    )


class CodannaMCPTool(BoilerplateBaseTool):
    """Codanna MCP를 LangChain Tool로 래핑.

    Docker 컨테이너로 실행되는 Codanna MCP와 JSON-RPC 통신.
    시맨틱 코드 검색 및 분석을 제공합니다.
    """

    name: str = "codanna_mcp"
    description: str = "시맨틱 코드 검색 및 분석. Docker MCP 서버 통신."
    args_schema: type[BaseModel] = CodannaMCPInput

    def _run(
        self,
        query: str,
        max_results: int = 10,
    ) -> dict[str, Any]:
        """Codanna MCP 도구를 실행합니다."""
        client = MCPDockerClient("codanna", project_path=self.project_root)

        result = client.call_tool("semantic_search", {
            "query": query,
            "max_results": max_results,
        })

        return result

    async def _arun(
        self,
        query: str,
        max_results: int = 10,
    ) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(query, max_results)
