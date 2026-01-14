"""코드 복잡도 분석 및 단순화 제안 도구."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field

from langchain_tools.tools.base import BoilerplateBaseTool
from langchain_tools.tools.stack_detector import StackDetectorTool


@dataclass
class ComplexitySuggestion:
    """복잡도 개선 제안."""

    type: Literal["long_function", "deep_nesting", "high_complexity"]
    file: str
    line: int
    message: str
    severity: Literal["high", "medium", "low"]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "file": self.file,
            "line": self.line,
            "message": self.message,
            "severity": self.severity,
        }


class SimplifierInput(BaseModel):
    """SimplifierTool 입력 스키마."""

    target_path: str | None = Field(
        default=None,
        description="분석할 디렉토리 경로. None이면 src/ 사용.",
    )


# 간결함 평가 기준 (Senior Engineer 관점)
SIMPLICITY_THRESHOLDS = {
    "max_function_lines": 50,      # 함수당 최대 라인 수
    "max_nesting_depth": 4,        # 최대 중첩 깊이
    "max_cyclomatic_complexity": 10,  # 최대 순환 복잡도
    "max_cognitive_complexity": 15,   # 최대 인지적 복잡도
}


class SimplifierTool(BoilerplateBaseTool):
    """코드 복잡도를 분석하고 단순화를 제안하는 도구.

    Senior Engineer의 관점에서 '간결함(Simplicity)'을 최우선 가치로 평가합니다.
    함수 길이, 중첩 깊이, 순환 복잡도를 분석합니다.
    """

    name: str = "simplifier"
    description: str = "코드 복잡도 분석 및 단순화 제안. 긴 함수, 깊은 중첩, 높은 복잡도를 감지합니다."
    args_schema: type[BaseModel] = SimplifierInput

    def _run(self, target_path: str | None = None) -> dict[str, Any]:
        """코드 복잡도를 분석합니다."""
        if target_path:
            analyze_path = Path(target_path).resolve()
        else:
            analyze_path = self.project_root / "src"

        if not analyze_path.exists():
            return {
                "status": "error",
                "message": f"Directory not found: {analyze_path}",
                "suggestions": [],
            }

        # 스택 감지
        stack_detector = StackDetectorTool(project_root=self.project_root)
        stack_info = stack_detector._run()

        suggestions: list[dict[str, Any]] = []

        if stack_info["stack"] == "python":
            suggestions = self._analyze_python(analyze_path)
        elif stack_info["stack"] == "node":
            suggestions = self._analyze_javascript(analyze_path)
        else:
            return {
                "status": "skipped",
                "message": f"Stack '{stack_info['stack']}' analysis not yet implemented",
                "suggestions": [],
            }

        # 심각도별 정렬
        severity_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: severity_order.get(x["severity"], 3))

        return {
            "status": "completed",
            "total_suggestions": len(suggestions),
            "suggestions": suggestions,
        }

    def _find_files(self, directory: Path, extensions: list[str]) -> list[Path]:
        """지정된 확장자를 가진 파일을 재귀적으로 찾습니다."""
        files: list[Path] = []

        for ext in extensions:
            files.extend(directory.rglob(f"*{ext}"))

        # node_modules, .venv 등 제외
        excluded = {"node_modules", ".venv", "venv", "__pycache__", ".git"}
        files = [f for f in files if not any(ex in f.parts for ex in excluded)]

        return files

    def _analyze_python(self, directory: Path) -> list[dict[str, Any]]:
        """Python 코드 복잡도 분석."""
        suggestions: list[dict[str, Any]] = []
        files = self._find_files(directory, [".py"])

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        suggestions.extend(
                            self._analyze_python_function(file_path, node, content)
                        )
            except SyntaxError:
                self._log_error(f"Syntax error in {file_path}")
            except Exception as e:
                self._log_error(f"Error analyzing {file_path}: {e}")

        return suggestions

    def _analyze_python_function(
        self,
        file_path: Path,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        content: str,
    ) -> list[dict[str, Any]]:
        """Python 함수 분석."""
        suggestions: list[dict[str, Any]] = []

        # 함수 라인 수 계산
        lines = content.split("\n")
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        line_count = end_line - start_line + 1

        if line_count > SIMPLICITY_THRESHOLDS["max_function_lines"]:
            suggestions.append({
                "type": "long_function",
                "file": str(file_path),
                "line": start_line,
                "message": (
                    f'Function "{node.name}" is {line_count} lines long '
                    f'(threshold: {SIMPLICITY_THRESHOLDS["max_function_lines"]}). '
                    "Consider splitting it into smaller functions."
                ),
                "severity": "medium",
            })

        # 중첩 깊이 분석
        max_depth = self._calculate_nesting_depth(node)
        if max_depth > SIMPLICITY_THRESHOLDS["max_nesting_depth"]:
            suggestions.append({
                "type": "deep_nesting",
                "file": str(file_path),
                "line": start_line,
                "message": (
                    f'Function "{node.name}" has nesting depth of {max_depth} '
                    f'(threshold: {SIMPLICITY_THRESHOLDS["max_nesting_depth"]}). '
                    "Consider refactoring to reduce nesting."
                ),
                "severity": "high",
            })

        # 순환 복잡도 계산
        complexity = self._calculate_cyclomatic_complexity(node)
        if complexity > SIMPLICITY_THRESHOLDS["max_cyclomatic_complexity"]:
            suggestions.append({
                "type": "high_complexity",
                "file": str(file_path),
                "line": start_line,
                "message": (
                    f'Function "{node.name}" has cyclomatic complexity of {complexity} '
                    f'(threshold: {SIMPLICITY_THRESHOLDS["max_cyclomatic_complexity"]}). '
                    "Consider simplifying the logic."
                ),
                "severity": "high",
            })

        return suggestions

    def _calculate_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """중첩 깊이를 계산합니다."""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._calculate_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)
            else:
                child_depth = self._calculate_nesting_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """순환 복잡도를 계산합니다."""
        complexity = 1  # 기본값

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1

        return complexity

    def _analyze_javascript(self, directory: Path) -> list[dict[str, Any]]:
        """JavaScript/TypeScript 코드 복잡도 분석."""
        suggestions: list[dict[str, Any]] = []
        files = self._find_files(directory, [".js", ".jsx", ".ts", ".tsx"])

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                suggestions.extend(self._analyze_js_content(file_path, content))
            except Exception as e:
                self._log_error(f"Error analyzing {file_path}: {e}")

        return suggestions

    def _analyze_js_content(self, file_path: Path, content: str) -> list[dict[str, Any]]:
        """JavaScript 파일 내용 분석."""
        suggestions: list[dict[str, Any]] = []
        lines = content.split("\n")

        # 함수 패턴
        function_patterns = [
            r"^(export\s+)?(async\s+)?function\s+(\w+)",
            r"^(export\s+)?const\s+(\w+)\s*=\s*(async\s+)?\(",
            r"^(export\s+)?(\w+)\s*:\s*(async\s+)?\(",
        ]

        current_function: str | None = None
        function_start: int = 0
        brace_count: int = 0

        for i, line in enumerate(lines):
            trimmed = line.strip()

            # 함수 시작 감지
            for pattern in function_patterns:
                match = re.match(pattern, trimmed)
                if match:
                    # 이전 함수 분석
                    if current_function and i - function_start > SIMPLICITY_THRESHOLDS["max_function_lines"]:
                        suggestions.append({
                            "type": "long_function",
                            "file": str(file_path),
                            "line": function_start + 1,
                            "message": (
                                f'Function "{current_function}" is {i - function_start} lines long '
                                f'(threshold: {SIMPLICITY_THRESHOLDS["max_function_lines"]}). '
                                "Consider splitting it into smaller functions."
                            ),
                            "severity": "medium",
                        })

                    current_function = match.group(2) if match.lastindex and match.lastindex >= 2 else "anonymous"
                    function_start = i
                    brace_count = 0
                    break

            # 중괄호 카운트
            brace_count += line.count("{") - line.count("}")

            # 중첩 깊이 체크
            if current_function and brace_count > SIMPLICITY_THRESHOLDS["max_nesting_depth"]:
                suggestions.append({
                    "type": "deep_nesting",
                    "file": str(file_path),
                    "line": i + 1,
                    "message": (
                        f"Nesting depth is {brace_count} "
                        f'(threshold: {SIMPLICITY_THRESHOLDS["max_nesting_depth"]}). '
                        "Consider refactoring to reduce nesting."
                    ),
                    "severity": "high",
                })

        return suggestions

    async def _arun(self, target_path: str | None = None) -> dict[str, Any]:
        """비동기 실행."""
        return self._run(target_path)
