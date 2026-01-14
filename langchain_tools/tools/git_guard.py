"""Git 규칙 검증 도구."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool


class GitGuardInput(BaseModel):
    """GitGuardTool 입력 스키마."""

    target_path: str | None = Field(
        default=None,
        description="검증할 Git 저장소 경로. None이면 현재 디렉토리 사용.",
    )


# Git Guide 규칙
BRANCH_PATTERNS = {
    "hotfix": re.compile(r'^hotfix/(\d+)-(.+)$'),
    "feature": re.compile(r'^feature/(\d+)-(.+)$'),
}

COMMIT_MESSAGE_PATTERN = re.compile(r'^Resolved\s+#(\d+)\s+-\s+(.+)$', re.IGNORECASE)


class GitGuardTool(BoilerplateBaseTool):
    """Git 규칙 준수를 검증하는 도구.

    브랜치 명명 규칙, 커밋 메시지 형식, Issue 번호 포함 여부 등을 확인합니다.
    """

    name: str = "git_guard"
    description: str = "Git 규칙 준수 검증. 브랜치명 형식, 커밋 메시지 형식, Issue 번호 포함 여부 확인."
    args_schema: type[BaseModel] = GitGuardInput

    def _run(self, target_path: str | None = None) -> dict[str, Any]:
        """Git 규칙을 검증합니다."""
        if target_path:
            project_path = Path(target_path).resolve()
        else:
            project_path = self.project_root

        result: dict[str, Any] = {
            "status": "passed",
            "checks": {
                "is_git_repository": False,
                "branch_name": {},
                "commit_message": {},
            },
            "violations": [],
        }

        # Git 저장소 확인
        git_dir = project_path / ".git"
        if not git_dir.exists():
            result["status"] = "error"
            result["checks"]["is_git_repository"] = False
            result["message"] = "Not a Git repository"
            return result

        result["checks"]["is_git_repository"] = True

        # 브랜치명 검증
        branch_result = self._validate_branch_name(project_path)
        result["checks"]["branch_name"] = branch_result
        if not branch_result.get("valid", False) and branch_result.get("current"):
            result["violations"].append({
                "type": "branch_name",
                "severity": "error",
                "message": branch_result.get("message", ""),
                "suggestion": "브랜치명을 다음 형식으로 변경하세요: feature/{issue_number}-{description} 또는 hotfix/{issue_number}-{description}",
            })

        # 커밋 메시지 검증
        commit_result = self._validate_commit_message(project_path)
        result["checks"]["commit_message"] = commit_result
        if not commit_result.get("valid", False) and commit_result.get("latest"):
            result["violations"].append({
                "type": "commit_message",
                "severity": "error",
                "message": commit_result.get("message", ""),
                "suggestion": "커밋 메시지를 다음 형식으로 변경하세요: Resolved #{Issue No} - {Description}",
            })

        # 상태 결정
        if any(v["severity"] == "error" for v in result["violations"]):
            result["status"] = "failed"
        elif result["violations"]:
            result["status"] = "warning"

        return result

    def _validate_branch_name(self, project_path: Path) -> dict[str, Any]:
        """브랜치명을 검증합니다."""
        try:
            proc = self._run_command(
                "git rev-parse --abbrev-ref HEAD",
                cwd=project_path,
            )
            branch_name = proc.stdout.strip() if proc.stdout else None
        except Exception:
            return {
                "valid": False,
                "message": "브랜치를 찾을 수 없습니다",
                "current": None,
                "issue_number": None,
            }

        if not branch_name:
            return {
                "valid": False,
                "message": "브랜치를 찾을 수 없습니다",
                "current": None,
                "issue_number": None,
            }

        # main, develop, master 브랜치는 검증 제외
        if branch_name in ("main", "develop", "master"):
            return {
                "valid": True,
                "message": "메인 브랜치는 검증 대상이 아닙니다",
                "current": branch_name,
                "issue_number": None,
            }

        # hotfix 또는 feature 패턴 확인
        for branch_type, pattern in BRANCH_PATTERNS.items():
            match = pattern.match(branch_name)
            if match:
                issue_number = match.group(1)
                description = match.group(2)
                return {
                    "valid": True,
                    "message": f"브랜치명이 규칙을 준수합니다 ({branch_type}/{issue_number}-{description})",
                    "current": branch_name,
                    "issue_number": issue_number,
                }

        return {
            "valid": False,
            "message": "브랜치명이 규칙을 준수하지 않습니다. 형식: hotfix/{issue_number}-{description} 또는 feature/{issue_number}-{description}",
            "current": branch_name,
            "issue_number": None,
        }

    def _validate_commit_message(self, project_path: Path) -> dict[str, Any]:
        """커밋 메시지를 검증합니다."""
        try:
            proc = self._run_command(
                "git log -1 --pretty=%B",
                cwd=project_path,
            )
            commit_message = proc.stdout.strip() if proc.stdout else None
        except Exception:
            return {
                "valid": False,
                "message": "커밋 메시지를 찾을 수 없습니다",
                "latest": None,
                "issue_number": None,
            }

        if not commit_message:
            return {
                "valid": False,
                "message": "커밋 메시지를 찾을 수 없습니다",
                "latest": None,
                "issue_number": None,
            }

        # 첫 번째 줄만 검증
        first_line = commit_message.split("\n")[0].strip()

        match = COMMIT_MESSAGE_PATTERN.match(first_line)
        if match:
            issue_number = match.group(1)
            description = match.group(2)
            return {
                "valid": True,
                "message": f"커밋 메시지가 규칙을 준수합니다 (Resolved #{issue_number} - {description})",
                "latest": first_line,
                "issue_number": issue_number,
            }

        return {
            "valid": False,
            "message": "커밋 메시지가 규칙을 준수하지 않습니다. 형식: Resolved #{Issue No} - {Description}",
            "latest": first_line,
            "issue_number": None,
        }

    async def _arun(self, target_path: str | None = None) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(target_path)
