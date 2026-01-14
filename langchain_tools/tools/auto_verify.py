"""자동 검증 도구."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool
from langchain_tools.tools.stack_detector import StackDetectorTool


class AutoVerifyInput(BaseModel):
    """AutoVerifyTool 입력 스키마."""

    target_path: str | None = Field(
        default=None,
        description="검증할 프로젝트 경로. None이면 현재 디렉토리 사용.",
    )


class AutoVerifyTool(BoilerplateBaseTool):
    """스택별 자동 검증을 실행하는 도구.

    Python: ruff check, ruff format, pytest
    Node.js: eslint, tsc, jest/vitest
    Go: go fmt, go vet, go test
    Rust: cargo fmt, cargo clippy, cargo test
    """

    name: str = "auto_verify"
    description: str = "스택별 자동 검증 실행 (린트, 포맷, 테스트). Python은 ruff/pytest, Node는 eslint/jest 사용."
    args_schema: type[BaseModel] = AutoVerifyInput

    def _run(self, target_path: str | None = None) -> dict[str, Any]:
        """자동 검증을 실행합니다."""
        if target_path:
            project_path = Path(target_path).resolve()
        else:
            project_path = self.project_root

        # 스택 감지
        stack_detector = StackDetectorTool(project_root=project_path)
        stack_info = stack_detector._run()

        results: dict[str, Any] = {
            "stack": stack_info["stack"],
            "package_manager": stack_info["package_manager"],
            "checks": {},
            "errors": [],
            "status": "passed",
        }

        stack = stack_info["stack"]

        if stack == "python":
            self._verify_python(project_path, stack_info, results)
        elif stack == "node":
            self._verify_node(project_path, stack_info, results)
        elif stack == "go":
            self._verify_go(project_path, results)
        elif stack == "rust":
            self._verify_rust(project_path, results)
        else:
            results["errors"].append(f"Unsupported stack: {stack}")
            results["status"] = "skipped"

        # 에러가 있으면 상태 업데이트
        if results["errors"]:
            results["status"] = "failed"

        return results

    def _verify_python(
        self,
        project_path: Path,
        stack_info: dict[str, Any],
        results: dict[str, Any],
    ) -> None:
        """Python 프로젝트 검증."""
        pm = stack_info["package_manager"]
        prefix = f"{pm} run" if pm in ("uv", "poetry") else ""

        # Ruff check
        try:
            cmd = f"{prefix} ruff check .".strip() if prefix else "ruff check ."
            result = self._run_command(cmd, cwd=project_path, timeout=60)
            results["checks"]["ruff_check"] = {
                "passed": result.returncode == 0,
                "output": result.stdout or result.stderr,
            }
            if result.returncode != 0:
                results["errors"].append("ruff check failed")
        except Exception as e:
            results["checks"]["ruff_check"] = {"passed": False, "error": str(e)}

        # Ruff format check
        try:
            cmd = f"{prefix} ruff format --check .".strip() if prefix else "ruff format --check ."
            result = self._run_command(cmd, cwd=project_path, timeout=60)
            results["checks"]["ruff_format"] = {
                "passed": result.returncode == 0,
                "output": result.stdout or result.stderr,
            }
        except Exception as e:
            results["checks"]["ruff_format"] = {"passed": False, "error": str(e)}

        # Pytest (if tests exist)
        tests_dir = project_path / "tests"
        if tests_dir.exists():
            try:
                cmd = f"{prefix} pytest .".strip() if prefix else "pytest ."
                result = self._run_command(cmd, cwd=project_path, timeout=120)
                results["checks"]["pytest"] = {
                    "passed": result.returncode == 0,
                    "output": result.stdout or result.stderr,
                }
                if result.returncode != 0:
                    results["errors"].append("pytest failed")
            except Exception as e:
                results["checks"]["pytest"] = {"passed": False, "error": str(e)}

    def _verify_node(
        self,
        project_path: Path,
        stack_info: dict[str, Any],
        results: dict[str, Any],
    ) -> None:
        """Node.js 프로젝트 검증."""
        pm = stack_info["package_manager"] or "npm"

        # ESLint
        eslint_config = any(
            (project_path / f).exists()
            for f in [".eslintrc.js", ".eslintrc.cjs", ".eslintrc.json", "eslint.config.js"]
        )

        if eslint_config:
            try:
                result = self._run_command(f"{pm} run lint", cwd=project_path, timeout=120)
                results["checks"]["eslint"] = {
                    "passed": result.returncode == 0,
                    "output": result.stdout or result.stderr,
                }
                if result.returncode != 0:
                    results["errors"].append("ESLint failed")
            except Exception as e:
                results["checks"]["eslint"] = {"passed": False, "error": str(e)}

        # TypeScript check
        if (project_path / "tsconfig.json").exists():
            try:
                run_cmd = "pnpm exec" if pm == "pnpm" else "npx"
                result = self._run_command(f"{run_cmd} tsc --noEmit", cwd=project_path, timeout=120)
                results["checks"]["typescript"] = {
                    "passed": result.returncode == 0,
                    "output": result.stdout or result.stderr,
                }
                if result.returncode != 0:
                    results["errors"].append("TypeScript check failed")
            except Exception as e:
                results["checks"]["typescript"] = {"passed": False, "error": str(e)}

        # Tests
        try:
            result = self._run_command(f"{pm} test", cwd=project_path, timeout=120)
            results["checks"]["test"] = {
                "passed": result.returncode == 0,
                "output": result.stdout or result.stderr,
            }
            if result.returncode != 0:
                results["errors"].append("Tests failed")
        except Exception as e:
            results["checks"]["test"] = {"passed": False, "error": str(e)}

    def _verify_go(self, project_path: Path, results: dict[str, Any]) -> None:
        """Go 프로젝트 검증."""
        # go fmt
        try:
            result = self._run_command("go fmt ./...", cwd=project_path, timeout=60)
            results["checks"]["go_fmt"] = {"passed": result.returncode == 0}
        except Exception as e:
            results["checks"]["go_fmt"] = {"passed": False, "error": str(e)}

        # go vet
        try:
            result = self._run_command("go vet ./...", cwd=project_path, timeout=60)
            results["checks"]["go_vet"] = {
                "passed": result.returncode == 0,
                "output": result.stdout or result.stderr,
            }
            if result.returncode != 0:
                results["errors"].append("go vet failed")
        except Exception as e:
            results["checks"]["go_vet"] = {"passed": False, "error": str(e)}

        # go test
        try:
            result = self._run_command("go test ./...", cwd=project_path, timeout=120)
            results["checks"]["go_test"] = {
                "passed": result.returncode == 0,
                "output": result.stdout or result.stderr,
            }
            if result.returncode != 0:
                results["errors"].append("go test failed")
        except Exception as e:
            results["checks"]["go_test"] = {"passed": False, "error": str(e)}

    def _verify_rust(self, project_path: Path, results: dict[str, Any]) -> None:
        """Rust 프로젝트 검증."""
        # cargo fmt check
        try:
            result = self._run_command("cargo fmt --check", cwd=project_path, timeout=60)
            results["checks"]["cargo_fmt"] = {"passed": result.returncode == 0}
        except Exception as e:
            results["checks"]["cargo_fmt"] = {"passed": False, "error": str(e)}

        # cargo clippy
        try:
            result = self._run_command("cargo clippy", cwd=project_path, timeout=120)
            results["checks"]["cargo_clippy"] = {
                "passed": result.returncode == 0,
                "output": result.stdout or result.stderr,
            }
            if result.returncode != 0:
                results["errors"].append("cargo clippy failed")
        except Exception as e:
            results["checks"]["cargo_clippy"] = {"passed": False, "error": str(e)}

        # cargo test
        try:
            result = self._run_command("cargo test", cwd=project_path, timeout=120)
            results["checks"]["cargo_test"] = {
                "passed": result.returncode == 0,
                "output": result.stdout or result.stderr,
            }
            if result.returncode != 0:
                results["errors"].append("cargo test failed")
        except Exception as e:
            results["checks"]["cargo_test"] = {"passed": False, "error": str(e)}

    async def _arun(self, target_path: str | None = None) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(target_path)
