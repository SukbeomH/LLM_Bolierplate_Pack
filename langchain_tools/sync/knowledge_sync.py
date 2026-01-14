"""CLAUDE.md 지식 동기화."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any


def extract_lessons_learned(content: str) -> list[dict[str, str]]:
    """CLAUDE.md에서 Lessons Learned 항목을 추출합니다."""
    lessons: list[dict[str, str]] = []

    # Lessons Learned 섹션 찾기
    pattern = r'####\s+\[(\d{4}-\d{2}-\d{2})\]\s+(.+?)(?=####|\Z)'
    matches = re.findall(pattern, content, re.DOTALL)

    for date, body in matches:
        lessons.append({
            "date": date,
            "content": body.strip(),
        })

    return lessons


def merge_lessons(
    source_lessons: list[dict[str, str]],
    dest_lessons: list[dict[str, str]],
) -> list[dict[str, str]]:
    """두 프로젝트의 Lessons Learned를 병합합니다."""
    # 날짜+내용 해시로 중복 감지
    seen = set()
    merged: list[dict[str, str]] = []

    for lesson in dest_lessons + source_lessons:
        key = f"{lesson['date']}:{lesson['content'][:100]}"
        if key not in seen:
            seen.add(key)
            merged.append(lesson)

    # 날짜 역순 정렬
    merged.sort(key=lambda x: x["date"], reverse=True)

    return merged


def format_lessons(lessons: list[dict[str, str]]) -> str:
    """Lessons Learned를 마크다운으로 포맷합니다."""
    lines: list[str] = []

    for lesson in lessons:
        lines.append(f"#### [{lesson['date']}] 동기화된 지식")
        lines.append("")
        lines.append(lesson["content"])
        lines.append("")

    return "\n".join(lines)


def sync_knowledge(
    source: Path,
    destination: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """소스 프로젝트의 CLAUDE.md 지식을 대상 프로젝트로 동기화합니다.

    Args:
        source: 소스 프로젝트 경로
        destination: 대상 프로젝트 경로
        dry_run: True면 실제 변경 없이 미리보기만

    Returns:
        동기화 결과 딕셔너리
    """
    result: dict[str, Any] = {
        "status": "success",
        "synced_count": 0,
        "message": "",
    }

    source_claude = source / "CLAUDE.md"
    dest_claude = destination / "CLAUDE.md"

    # 파일 존재 확인
    if not source_claude.exists():
        result["status"] = "failed"
        result["message"] = f"소스 CLAUDE.md를 찾을 수 없습니다: {source_claude}"
        return result

    if not dest_claude.exists():
        result["status"] = "failed"
        result["message"] = f"대상 CLAUDE.md를 찾을 수 없습니다: {dest_claude}"
        return result

    try:
        source_content = source_claude.read_text(encoding="utf-8")
        dest_content = dest_claude.read_text(encoding="utf-8")

        # Lessons Learned 추출
        source_lessons = extract_lessons_learned(source_content)
        dest_lessons = extract_lessons_learned(dest_content)

        if not source_lessons:
            result["message"] = "소스에 동기화할 Lessons Learned가 없습니다"
            return result

        # 병합
        merged = merge_lessons(source_lessons, dest_lessons)
        new_count = len(merged) - len(dest_lessons)

        if new_count <= 0:
            result["message"] = "동기화할 새로운 Lessons Learned가 없습니다"
            return result

        # Lessons Learned 섹션 교체
        lessons_section = format_lessons(merged)

        # 기존 Lessons Learned 섹션 찾아서 교체
        pattern = r'(### 📚 Lessons Learned.*?\n\n).*?(?=\n## |\Z)'
        replacement = f"\\1{lessons_section}"

        if re.search(pattern, dest_content, re.DOTALL):
            new_content = re.sub(pattern, replacement, dest_content, flags=re.DOTALL)
        else:
            # 섹션이 없으면 끝에 추가
            new_content = dest_content + f"\n\n### 📚 Lessons Learned\n\n{lessons_section}"

        if not dry_run:
            dest_claude.write_text(new_content, encoding="utf-8")

        result["synced_count"] = new_count
        result["message"] = f"{new_count}개의 새로운 Lessons Learned 동기화됨"

    except Exception as e:
        result["status"] = "failed"
        result["message"] = str(e)

    return result
