"""도구별 설치 가이드 생성."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def generate_setup_guide(
    target: Path,
    *,
    tool_filter: str = "all",
) -> str:
    """도구별 MCP 설정 가이드를 생성합니다.

    Args:
        target: 프로젝트 경로
        tool_filter: "all", "claude-code", "cursor", "claude-desktop", "vscode"

    Returns:
        설정 가이드 문자열
    """
    mcp_json = target / ".mcp.json"
    cursor_json = target / ".cursor" / "mcp.json"

    lines: list[str] = []
    lines.append("📋 도구별 프로젝트 MCP 설정 가이드")
    lines.append("=" * 50)
    lines.append("")

    # Claude Code
    if tool_filter in ("all", "claude-code"):
        lines.append("🔹 Claude Code")
        if mcp_json.exists():
            lines.append("   ✅ 자동 인식됨 (.mcp.json)")
        else:
            lines.append("   ⚠️ .mcp.json 파일이 없습니다")
            lines.append("   → `uv run python -m langchain_tools.cli inject` 실행")
        lines.append("")

    # Cursor IDE
    if tool_filter in ("all", "cursor"):
        lines.append("🔹 Cursor IDE")
        if cursor_json.exists():
            lines.append("   ✅ 프로젝트 설정 (.cursor/mcp.json)")
            lines.append("   → Settings > Features > MCP에서 프로젝트 설정 활성화")
        else:
            lines.append("   ⚠️ .cursor/mcp.json 파일이 없습니다")
            lines.append("   → `uv run python -m langchain_tools.cli inject` 실행")
        lines.append("")

    # Claude Desktop
    if tool_filter in ("all", "claude-desktop"):
        lines.append("🔹 Claude Desktop (수동 설정 필요)")
        lines.append("")
        if mcp_json.exists():
            try:
                config = json.loads(mcp_json.read_text(encoding="utf-8"))
                config_str = json.dumps(config, indent=2, ensure_ascii=False)
                lines.append("   아래 설정을 claude_desktop_config.json에 복사:")
                lines.append("")
                lines.append("   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
                lines.append("   Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
                lines.append("")
                lines.append("   ```json")
                for line in config_str.split("\n"):
                    lines.append(f"   {line}")
                lines.append("   ```")
            except Exception:
                lines.append("   ⚠️ .mcp.json 파싱 실패")
        else:
            lines.append("   ⚠️ .mcp.json 파일이 없습니다")
        lines.append("")

    # VS Code
    if tool_filter in ("all", "vscode"):
        lines.append("🔹 VS Code (GitHub Copilot)")
        if mcp_json.exists():
            lines.append("   ✅ 자동 인식됨 (.mcp.json)")
        else:
            lines.append("   ⚠️ .mcp.json 파일이 없습니다")
        lines.append("")

    # Google Antigravity
    if tool_filter in ("all", "antigravity"):
        lines.append("🔹 Google Antigravity")
        if mcp_json.exists():
            lines.append("   ✅ .mcp.json 자동 인식됨")
            lines.append("   → Agent Manager에서 MCP 서버 활성화")
        else:
            lines.append("   ⚠️ .mcp.json 파일이 없습니다")
        lines.append("")

    return "\n".join(lines)
