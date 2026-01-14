"""공통 베이스 클래스 및 유틸리티."""

from __future__ import annotations

import os
import subprocess
import logging
from abc import ABC
from pathlib import Path
from typing import Any

from langchain.tools import BaseTool
from pydantic import Field


logger = logging.getLogger(__name__)


def find_project_root(start_path: Path | None = None) -> Path:
    """프로젝트 루트 디렉토리를 찾습니다.

    .git, pyproject.toml, package.json 등의 마커 파일을 기반으로 탐지합니다.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()
    markers = [".git", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]

    while current != current.parent:
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent

    return start_path


def run_shell_command(
    command: str | list[str],
    cwd: Path | str | None = None,
    timeout: int = 120,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    """셸 명령을 실행합니다.

    Args:
        command: 실행할 명령 (문자열 또는 리스트)
        cwd: 작업 디렉토리
        timeout: 타임아웃 (초)
        capture_output: 출력 캡처 여부

    Returns:
        실행 결과
    """
    if isinstance(command, str):
        shell = True
    else:
        shell = False

    return subprocess.run(
        command,
        cwd=cwd,
        shell=shell,
        capture_output=capture_output,
        text=True,
        timeout=timeout,
    )


class BoilerplateBaseTool(BaseTool, ABC):
    """Boilerplate 도구의 베이스 클래스.

    프로젝트 루트 탐지, 로깅 설정 등 공통 기능을 제공합니다.
    """

    project_root: Path = Field(default_factory=find_project_root)

    class Config:
        arbitrary_types_allowed = True

    def _run_command(
        self,
        command: str | list[str],
        cwd: Path | str | None = None,
        timeout: int = 120,
    ) -> subprocess.CompletedProcess[str]:
        """명령을 실행합니다."""
        if cwd is None:
            cwd = self.project_root
        return run_shell_command(command, cwd=cwd, timeout=timeout)

    def _log_info(self, message: str) -> None:
        """정보 메시지를 로깅합니다."""
        logger.info(f"[{self.name}] {message}")

    def _log_error(self, message: str) -> None:
        """에러 메시지를 로깅합니다."""
        logger.error(f"[{self.name}] {message}")
