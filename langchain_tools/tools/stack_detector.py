"""스택 감지 도구."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool


class StackInfo(BaseModel):
    """감지된 스택 정보."""

    stack: Literal["python", "node", "go", "rust", "unknown"]
    package_manager: str | None = None
    venv_path: str | None = None
    has_uv_lock: bool = False
    has_poetry_lock: bool = False
    has_package_json: bool = False
    has_pnpm_lock: bool = False


class StackDetectorInput(BaseModel):
    """StackDetectorTool 입력 스키마."""

    target_path: str | None = Field(
        default=None,
        description="분석할 프로젝트 경로. None이면 현재 디렉토리 사용.",
    )


class StackDetectorTool(BoilerplateBaseTool):
    """프로젝트 스택을 감지하는 도구.

    Python, Node.js, Go, Rust 등의 스택을 감지하고 패키지 매니저 정보를 반환합니다.
    """

    name: str = "stack_detector"
    description: str = "프로젝트 스택 감지 (Python/Node.js/Go/Rust). 패키지 매니저 및 가상환경 정보 포함."
    args_schema: type[BaseModel] = StackDetectorInput

    def _run(self, target_path: str | None = None) -> dict[str, Any]:
        """스택을 감지합니다."""
        if target_path:
            project_path = Path(target_path).resolve()
        else:
            project_path = self.project_root

        return self._detect_stack(project_path)

    def _detect_stack(self, project_path: Path) -> dict[str, Any]:
        """프로젝트 스택을 감지합니다."""
        result: dict[str, Any] = {
            "stack": "unknown",
            "package_manager": None,
            "venv_path": None,
            "has_uv_lock": False,
            "has_poetry_lock": False,
            "has_package_json": False,
            "has_pnpm_lock": False,
        }

        # 파일 존재 여부 확인
        uv_lock = project_path / "uv.lock"
        poetry_lock = project_path / "poetry.lock"
        pyproject = project_path / "pyproject.toml"
        package_json = project_path / "package.json"
        pnpm_lock = project_path / "pnpm-lock.yaml"
        npm_lock = project_path / "package-lock.json"
        go_mod = project_path / "go.mod"
        cargo_toml = project_path / "Cargo.toml"

        result["has_uv_lock"] = uv_lock.exists()
        result["has_poetry_lock"] = poetry_lock.exists()
        result["has_package_json"] = package_json.exists()
        result["has_pnpm_lock"] = pnpm_lock.exists()

        # Python 스택 감지
        if uv_lock.exists() or poetry_lock.exists() or pyproject.exists():
            result["stack"] = "python"

            if uv_lock.exists():
                result["package_manager"] = "uv"
            elif poetry_lock.exists():
                result["package_manager"] = "poetry"
            else:
                result["package_manager"] = "pip"

            # 가상 환경 경로 감지
            for venv_name in [".venv", "venv", ".virtualenv"]:
                venv_path = project_path / venv_name
                if venv_path.exists():
                    result["venv_path"] = str(venv_path)
                    break

        # Node.js 스택 감지 (Python이 아닌 경우)
        elif package_json.exists():
            result["stack"] = "node"

            if pnpm_lock.exists():
                result["package_manager"] = "pnpm"
            elif npm_lock.exists():
                result["package_manager"] = "npm"
            elif (project_path / "yarn.lock").exists():
                result["package_manager"] = "yarn"
            else:
                result["package_manager"] = "npm"

        # Go 스택 감지
        elif go_mod.exists():
            result["stack"] = "go"
            result["package_manager"] = "go"

        # Rust 스택 감지
        elif cargo_toml.exists():
            result["stack"] = "rust"
            result["package_manager"] = "cargo"

        self._log_info(f"Detected stack: {result['stack']} ({result['package_manager']})")
        return result

    async def _arun(self, target_path: str | None = None) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(target_path)
