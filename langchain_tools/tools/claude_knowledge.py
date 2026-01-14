"""CLAUDE.md 지식 업데이트 도구."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool


class ClaudeKnowledgeInput(BaseModel):
    """ClaudeKnowledgeUpdaterTool 입력 스키마."""

    verification_result: dict[str, Any] = Field(
        description="검증 피드백 루프 결과 JSON",
    )
    target_path: str | None = Field(
        default=None,
        description="프로젝트 경로. None이면 현재 디렉토리 사용.",
    )


class ClaudeKnowledgeUpdaterTool(BoilerplateBaseTool):
    """CLAUDE.md의 Lessons Learned 섹션을 업데이트하는 도구.

    검증 피드백 루프 결과를 마크다운 형식으로 변환하여
    지식이 복리로 축적되도록 합니다.
    """

    name: str = "claude_knowledge_updater"
    description: str = "CLAUDE.md Lessons Learned 섹션 업데이트. 검증 결과를 마크다운으로 변환하여 추가."
    args_schema: type[BaseModel] = ClaudeKnowledgeInput

    def _run(
        self,
        verification_result: dict[str, Any],
        target_path: str | None = None,
    ) -> dict[str, Any]:
        """CLAUDE.md를 업데이트합니다."""
        if target_path:
            project_path = Path(target_path).resolve()
        else:
            project_path = self.project_root

        claude_md = project_path / "CLAUDE.md"

        if not claude_md.exists():
            return {
                "status": "error",
                "message": f"CLAUDE.md not found at {claude_md}",
            }

        try:
            content = claude_md.read_text(encoding="utf-8")

            # Lessons Learned 섹션 확인 및 추가
            content = self._ensure_lessons_learned_section(content)

            # 새 엔트리 생성
            new_entry = self._format_verification_result(verification_result)

            # 섹션에 추가
            content = self._add_entry_to_lessons_learned(content, new_entry)

            # 파일 저장
            claude_md.write_text(content, encoding="utf-8")

            self._log_info("CLAUDE.md updated successfully")
            return {
                "status": "success",
                "message": "CLAUDE.md updated successfully",
            }
        except Exception as e:
            self._log_error(f"Failed to update CLAUDE.md: {e}")
            return {
                "status": "error",
                "message": str(e),
            }

    def _format_verification_result(self, result: dict[str, Any]) -> str:
        """검증 결과를 마크다운 형식으로 변환합니다."""
        date = datetime.now().strftime("%Y-%m-%d")
        markdown = f"\n#### [{date}] 검증 피드백 루프 실행 결과\n"

        steps = result.get("steps", {})
        verify = steps.get("verify", {})

        # 코드 단순화 제안
        simplifier = verify.get("simplifier", {})
        suggestions = simplifier.get("suggestions", [])
        if suggestions:
            markdown += f"- **코드 복잡도 분석**: {len(suggestions)}개의 개선 제안 발견\n"
            for suggestion in suggestions[:3]:
                msg = suggestion.get("message", "").replace("\n", " ")[:100]
                markdown += f"  - {suggestion.get('type', 'unknown')}: {msg}\n"

        # 기본 검증 에러
        basic = verify.get("basic", {})
        errors = basic.get("errors", [])
        if errors:
            markdown += f"- **검증 에러**: {len(errors)}개의 에러 발견\n"
            for error in errors[:3]:
                markdown += f"  - {error}\n"

        # 보안 감사 결과
        security = verify.get("security", {})
        vulns = security.get("vulnerabilities", [])
        if vulns:
            markdown += f"- **보안 감사**: {len(vulns)}개의 취약점 발견\n"
            for vuln in vulns[:3]:
                name = vuln.get("name") or vuln.get("title") or "Unknown"
                severity = vuln.get("severity", "Unknown severity")
                markdown += f"  - {name}: {severity}\n"
        elif security.get("status") == "secure":
            markdown += "- **보안 감사**: 취약점 없음\n"
        elif security.get("status") == "error":
            markdown += "- **보안 감사**: 실패 (도구 미설치 또는 오류)\n"

        # 승인 상태
        approve = steps.get("approve", {})
        status = approve.get("status", "skipped")
        if status == "approved":
            markdown += "- **적용 여부**: 승인됨\n"
        elif status == "rejected":
            markdown += "- **적용 여부**: 거부됨\n"
        else:
            markdown += "- **적용 여부**: 건너뜀\n"

        return markdown

    def _ensure_lessons_learned_section(self, content: str) -> str:
        """Lessons Learned 섹션이 있는지 확인하고 없으면 추가합니다."""
        if "### 📚 Lessons Learned" in content:
            return content

        # Compounding Knowledge 섹션 찾기
        pattern = r'(## 🧠 Compounding Knowledge[^#]*)'
        match = re.search(pattern, content, re.DOTALL)

        lessons_section = (
            "\n### 📚 Lessons Learned (자동 업데이트)\n\n"
            "이 섹션은 검증 피드백 루프 실행 결과가 자동으로 추가됩니다.\n\n"
        )

        if match:
            # Compounding Knowledge 섹션 끝에 추가
            insert_pos = match.end()
            return content[:insert_pos] + lessons_section + content[insert_pos:]
        else:
            # 파일 끝에 새 섹션 추가
            return content + (
                "\n\n## 🧠 Compounding Knowledge (복리 지식)\n\n"
                "이 섹션은 팀의 실전 경험이 축적되는 공간입니다.\n"
                + lessons_section
            )

    def _add_entry_to_lessons_learned(self, content: str, entry: str) -> str:
        """Lessons Learned 섹션에 새 엔트리를 추가합니다."""
        pattern = r'(### 📚 Lessons Learned \(자동 업데이트\)[^\n]*\n)'
        match = re.search(pattern, content)

        if match:
            insert_pos = match.end()
            # 기존 설명 텍스트 건너뛰기
            remaining = content[insert_pos:]
            desc_end = remaining.find("\n\n")
            if desc_end > 0:
                insert_pos += desc_end + 2
            return content[:insert_pos] + entry + content[insert_pos:]

        return content + entry

    async def _arun(
        self,
        verification_result: dict[str, Any],
        target_path: str | None = None,
    ) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(verification_result, target_path)
