"""보안 감사 도구."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool
from langchain_tools.tools.stack_detector import StackDetectorTool


class SecurityAuditInput(BaseModel):
    """SecurityAuditTool 입력 스키마."""

    target_path: str | None = Field(
        default=None,
        description="감사할 프로젝트 경로. None이면 현재 디렉토리 사용.",
    )


class SecurityAuditTool(BoilerplateBaseTool):
    """보안 감사를 실행하는 도구.

    Python: safety check 또는 pip-audit 실행
    Node.js: npm audit 또는 pnpm audit 실행
    """

    name: str = "security_audit"
    description: str = "보안 감사 실행. Python은 safety check, Node는 npm/pnpm audit 사용."
    args_schema: type[BaseModel] = SecurityAuditInput

    def _run(self, target_path: str | None = None) -> dict[str, Any]:
        """보안 감사를 실행합니다."""
        if target_path:
            project_path = Path(target_path).resolve()
        else:
            project_path = self.project_root

        # 스택 감지
        stack_detector = StackDetectorTool(project_root=project_path)
        stack_info = stack_detector._run()

        stack = stack_info["stack"]

        if stack == "python":
            return self._audit_python(project_path, stack_info)
        elif stack == "node":
            return self._audit_node(project_path, stack_info)
        else:
            return {
                "stack": stack,
                "status": "not_supported",
                "message": f"Security audit not supported for stack: {stack}",
                "vulnerabilities": [],
            }

    def _audit_python(
        self,
        project_path: Path,
        stack_info: dict[str, Any],
    ) -> dict[str, Any]:
        """Python 프로젝트 보안 감사."""
        result: dict[str, Any] = {
            "stack": "python",
            "tool": "safety",
            "status": "unknown",
            "vulnerabilities": [],
            "errors": [],
        }

        pm = stack_info["package_manager"]

        # 명령어 결정
        if pm == "uv":
            cmd = "uv run pip-audit --json"
        elif pm == "poetry":
            cmd = "poetry run safety check --json"
        else:
            cmd = "safety check --json"

        try:
            proc = self._run_command(cmd, cwd=project_path, timeout=120)

            try:
                # JSON 파싱 시도
                output = proc.stdout or ""
                if output.strip():
                    data = json.loads(output)
                    if isinstance(data, list) and len(data) > 0:
                        result["status"] = "vulnerable"
                        result["vulnerabilities"] = data[:20]  # 최대 20개
                        self._log_info(f"Found {len(data)} vulnerability(ies)")
                    else:
                        result["status"] = "secure"
                        self._log_info("No vulnerabilities found")
                else:
                    result["status"] = "secure" if proc.returncode == 0 else "error"
            except json.JSONDecodeError:
                # 텍스트 출력 분석
                if "No known security vulnerabilities" in (proc.stdout or ""):
                    result["status"] = "secure"
                elif proc.returncode != 0:
                    result["status"] = "vulnerable"
                    result["errors"].append("Could not parse audit output")
                else:
                    result["status"] = "secure"
        except FileNotFoundError:
            result["status"] = "tool_not_found"
            result["errors"].append(f"Safety/pip-audit not found. Install with: {pm} add safety --dev")
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))

        return result

    def _audit_node(
        self,
        project_path: Path,
        stack_info: dict[str, Any],
    ) -> dict[str, Any]:
        """Node.js 프로젝트 보안 감사."""
        result: dict[str, Any] = {
            "stack": "node",
            "tool": stack_info["package_manager"] or "npm",
            "status": "unknown",
            "vulnerabilities": [],
            "errors": [],
        }

        pm = stack_info["package_manager"] or "npm"
        cmd = f"{pm} audit --json"

        try:
            proc = self._run_command(cmd, cwd=project_path, timeout=120)

            try:
                output = proc.stdout or ""
                if output.strip():
                    data = json.loads(output)

                    # npm audit JSON 구조 분석
                    vulns = data.get("vulnerabilities", {})
                    if isinstance(vulns, dict) and len(vulns) > 0:
                        result["status"] = "vulnerable"
                        result["vulnerabilities"] = [
                            {
                                "name": name,
                                "severity": info.get("severity", "unknown"),
                                "title": info.get("title", ""),
                                "url": info.get("url", ""),
                            }
                            for name, info in list(vulns.items())[:20]
                        ]
                        self._log_info(f"Found {len(vulns)} vulnerability(ies)")
                    elif "metadata" in data:
                        total = data.get("metadata", {}).get("vulnerabilities", {}).get("total", 0)
                        if total > 0:
                            result["status"] = "vulnerable"
                        else:
                            result["status"] = "secure"
                    else:
                        result["status"] = "secure"
                else:
                    result["status"] = "secure" if proc.returncode == 0 else "error"
            except json.JSONDecodeError:
                result["status"] = "error"
                result["errors"].append("Could not parse audit output")
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))

        return result

    async def _arun(self, target_path: str | None = None) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(target_path)
