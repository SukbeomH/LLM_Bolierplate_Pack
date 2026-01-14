"""시각적 검증 도구."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool
from langchain_tools.tools.stack_detector import StackDetectorTool


class VisualVerifierInput(BaseModel):
    """VisualVerifierTool 입력 스키마."""

    target_path: str | None = Field(
        default=None,
        description="프로젝트 경로. None이면 현재 디렉토리 사용.",
    )
    port: int = Field(
        default=3000,
        description="개발 서버 포트 번호.",
    )


class VisualVerifierTool(BoilerplateBaseTool):
    """웹 프로젝트의 시각적 검증을 지원하는 도구.

    Chrome DevTools MCP와 연계하여 렌더링 및 네트워크 문제를 검증하기 위한
    가이드를 생성합니다.
    """

    name: str = "visual_verifier"
    description: str = "웹 프로젝트 시각적 검증 가이드 생성. 콘솔 에러, 네트워크 에러, 렌더링 문제 체크리스트 제공."
    args_schema: type[BaseModel] = VisualVerifierInput

    def _run(
        self,
        target_path: str | None = None,
        port: int = 3000,
    ) -> dict[str, Any]:
        """시각적 검증 가이드를 생성합니다."""
        if target_path:
            project_path = Path(target_path).resolve()
        else:
            project_path = self.project_root

        # 스택 감지
        stack_detector = StackDetectorTool(project_root=project_path)
        stack_info = stack_detector._run()

        if stack_info["stack"] != "node":
            return {
                "status": "skipped",
                "message": "Visual verification is only applicable to web projects (Node.js)",
                "guide": None,
            }

        # 웹 프로젝트 확인
        if not self._is_web_project(project_path):
            return {
                "status": "skipped",
                "message": "Not a web project (no web framework detected)",
                "guide": None,
            }

        url = f"http://localhost:{port}"
        guide = self._generate_mcp_verification_guide(url, port)

        return {
            "status": "ready",
            "url": url,
            "guide": guide,
            "message": "Visual verification guide generated. Use Chrome DevTools MCP to execute the verification steps.",
        }

    def _is_web_project(self, project_path: Path) -> bool:
        """웹 프로젝트인지 확인합니다."""
        package_json = project_path / "package.json"
        if not package_json.exists():
            return False

        try:
            data = json.loads(package_json.read_text(encoding="utf-8"))
            deps = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
            }

            web_frameworks = [
                "react", "vue", "angular", "svelte",
                "next", "nuxt", "remix", "sveltekit",
                "express", "fastify", "koa",
                "vite", "webpack",
            ]

            return any(fw in deps or f"@{fw}" in deps for fw in web_frameworks)
        except (json.JSONDecodeError, IOError):
            return False

    def _generate_mcp_verification_guide(
        self,
        url: str,
        port: int,
    ) -> dict[str, Any]:
        """Chrome DevTools MCP 검증 가이드를 생성합니다."""
        return {
            "url": url,
            "port": port,
            "steps": [
                {
                    "step": 1,
                    "action": "Navigate to URL",
                    "mcp_tool": "browser_navigate",
                    "description": f"Navigate to {url}",
                },
                {
                    "step": 2,
                    "action": "Take snapshot",
                    "mcp_tool": "browser_snapshot",
                    "description": "Capture accessibility snapshot to check for rendering errors",
                },
                {
                    "step": 3,
                    "action": "Check console messages",
                    "mcp_tool": "browser_console_messages",
                    "description": "Check for JavaScript errors, React/Vue errors, or warnings",
                },
                {
                    "step": 4,
                    "action": "Analyze network requests",
                    "mcp_tool": "browser_network_requests",
                    "description": "Check for 4xx/5xx errors, slow requests (>500ms), or unnecessary API calls",
                },
            ],
            "checks": {
                "console_errors": {
                    "description": "No JavaScript errors should be present in console",
                    "severity": "high",
                },
                "network_errors": {
                    "description": "No 4xx/5xx HTTP errors should be present",
                    "severity": "high",
                },
                "slow_requests": {
                    "description": "Requests should complete within 500ms",
                    "severity": "medium",
                },
                "rendering_issues": {
                    "description": "No layout breaking or image load failures",
                    "severity": "high",
                },
            },
        }

    async def _arun(
        self,
        target_path: str | None = None,
        port: int = 3000,
    ) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(target_path, port)
