"""로그 분석 도구."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool


@dataclass
class LogEntry:
    """파싱된 로그 항목."""

    timestamp: str
    levelname: str
    name: str
    thread_info: str
    module: str | None
    func_name: str | None
    lineno: int | None
    message: str
    raw: str
    line_number: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "levelname": self.levelname,
            "name": self.name,
            "module": self.module,
            "func_name": self.func_name,
            "lineno": self.lineno,
            "message": self.message,
            "line_number": self.line_number,
        }


class LogAnalyzerInput(BaseModel):
    """LogAnalyzerTool 입력 스키마."""

    log_file: str | None = Field(
        default=None,
        description="분석할 로그 파일 경로. None이면 app.log 사용.",
    )
    target_path: str | None = Field(
        default=None,
        description="프로젝트 경로. None이면 현재 디렉토리 사용.",
    )


# 민감 정보 마스킹 패턴
SENSITIVE_PATTERNS = [
    re.compile(r'\b(password|pwd|secret|token|api[_-]?key|auth[_-]?token|access[_-]?token)\s*[:=]\s*[\'"]?([^\s\'"]+)[\'"]?', re.IGNORECASE),
    re.compile(r'\b(email|phone|ssn|credit[_-]?card)\s*[:=]\s*[\'"]?([^\s\'"]+)[\'"]?', re.IGNORECASE),
    re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),  # Credit card numbers
]

# 로그 라인 패턴 (logging.conf 포맷)
LOG_PATTERN = re.compile(
    r'^\[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] \[([^\]]+)\] - (.+)$'
)


class LogAnalyzerTool(BoilerplateBaseTool):
    """로그 파일을 분석하는 도구.

    logging.conf 포맷의 로그를 파싱하여 ERROR/CRITICAL 로그를 감지합니다.
    민감 정보는 자동으로 마스킹됩니다.
    """

    name: str = "log_analyzer"
    description: str = "로그 파일 분석. ERROR/CRITICAL 로그 감지 및 코드 분석 가이드 생성."
    args_schema: type[BaseModel] = LogAnalyzerInput

    def _run(
        self,
        log_file: str | None = None,
        target_path: str | None = None,
    ) -> dict[str, Any]:
        """로그를 분석합니다."""
        if target_path:
            project_path = Path(target_path).resolve()
        else:
            project_path = self.project_root

        if log_file:
            log_path = Path(log_file).resolve()
        else:
            log_path = project_path / "app.log"

        return self._analyze_log_file(log_path)

    def _mask_sensitive_info(self, text: str) -> str:
        """민감 정보를 마스킹합니다."""
        masked = text
        for pattern in SENSITIVE_PATTERNS:
            masked = pattern.sub(
                lambda m: f"{m.group(1)}={'*' * min(len(m.group(2)) if m.lastindex and m.lastindex >= 2 else 8, 8)}"
                if m.lastindex and m.lastindex >= 2
                else '*' * 16,
                masked
            )
        return masked

    def _parse_log_line(self, line: str) -> LogEntry | None:
        """로그 라인을 파싱합니다."""
        match = LOG_PATTERN.match(line)
        if not match:
            return None

        timestamp, levelname, name, thread_info, location, message = match.groups()

        # location에서 module:funcName:lineno 추출
        location_match = re.match(r'^([^:]+):([^:]+):(\d+)$', location)
        module = location_match.group(1) if location_match else None
        func_name = location_match.group(2) if location_match else None
        lineno = int(location_match.group(3)) if location_match else None

        return LogEntry(
            timestamp=timestamp,
            levelname=levelname.strip(),
            name=name.strip(),
            thread_info=thread_info.strip(),
            module=module,
            func_name=func_name,
            lineno=lineno,
            message=self._mask_sensitive_info(message.strip()),
            raw=self._mask_sensitive_info(line),
            line_number=0,  # 나중에 설정
        )

    def _analyze_log_file(self, log_path: Path) -> dict[str, Any]:
        """로그 파일을 분석합니다."""
        result: dict[str, Any] = {
            "total_lines": 0,
            "errors": [],
            "criticals": [],
            "warnings": [],
            "summary": {
                "error_count": 0,
                "critical_count": 0,
                "warning_count": 0,
                "has_severe_errors": False,
            },
            "code_analysis_guides": [],
            "status": "passed",
        }

        if not log_path.exists():
            result["status"] = "skipped"
            result["message"] = f"Log file not found: {log_path}"
            self._log_info(f"Log file not found: {log_path}")
            return result

        try:
            content = log_path.read_text(encoding="utf-8")
            lines = [l for l in content.split("\n") if l.strip()]
            result["total_lines"] = len(lines)

            for i, line in enumerate(lines):
                parsed = self._parse_log_line(line)
                if not parsed:
                    continue

                parsed.line_number = i + 1
                level = parsed.levelname.upper()

                if level == "ERROR":
                    result["errors"].append(parsed.to_dict())
                    result["summary"]["error_count"] += 1
                elif level == "CRITICAL":
                    result["criticals"].append(parsed.to_dict())
                    result["summary"]["critical_count"] += 1
                elif level == "WARNING":
                    result["warnings"].append(parsed.to_dict())
                    result["summary"]["warning_count"] += 1

            result["summary"]["has_severe_errors"] = (
                result["summary"]["error_count"] > 0 or
                result["summary"]["critical_count"] > 0
            )

            # 상태 설정
            if result["summary"]["has_severe_errors"]:
                result["status"] = "failed"

            # 코드 분석 가이드 생성
            for entry in result["errors"][:5] + result["criticals"][:5]:
                result["code_analysis_guides"].append(
                    self._generate_code_analysis_guide(entry)
                )

            # 결과 제한 (최근 10개)
            result["errors"] = result["errors"][:10]
            result["criticals"] = result["criticals"][:10]
            result["warnings"] = result["warnings"][:10]

        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
            self._log_error(f"Failed to read log file: {e}")

        return result

    def _generate_code_analysis_guide(self, log_entry: dict[str, Any]) -> dict[str, Any]:
        """코드 분석 가이드를 생성합니다."""
        guides: list[dict[str, str]] = []

        module = log_entry.get("module")
        func_name = log_entry.get("func_name")
        lineno = log_entry.get("lineno")
        message = log_entry.get("message", "")

        if module and func_name and lineno:
            guides.append({
                "tool": "semantic_search",
                "query": f"Error in {module}.{func_name} at line {lineno}: {message}",
                "description": f"Search for related code patterns and error handling in {module}",
            })
            guides.append({
                "tool": "find_symbol",
                "query": f"{module}/{func_name}",
                "description": f"Find the exact symbol definition for {func_name} in {module}",
            })
        else:
            guides.append({
                "tool": "semantic_search",
                "query": message,
                "description": f"Search for code patterns related to error message: {message[:100]}",
            })

        return {
            "log_entry": {
                "timestamp": log_entry.get("timestamp"),
                "level": log_entry.get("levelname"),
                "module": module,
                "func_name": func_name,
                "lineno": lineno,
                "message": message,
            },
            "analysis_guides": guides,
        }

    async def _arun(
        self,
        log_file: str | None = None,
        target_path: str | None = None,
    ) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(log_file, target_path)
