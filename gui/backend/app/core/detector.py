"""
스택 감지 로직

detect_stack.sh를 실행하여 프로젝트의 스택을 감지합니다.
"""

import subprocess
import os
import re
from pathlib import Path
from typing import Dict, Optional, List, Any
import json


class StackDetector:
	"""스택 감지 클래스"""

	def __init__(self, boilerplate_root: Path):
		"""
		초기화

		Args:
			boilerplate_root: 보일러플레이트 프로젝트 루트 경로
		"""
		self.boilerplate_root = boilerplate_root
		self.detect_script = boilerplate_root / "scripts" / "core" / "detect_stack.sh"

	def detect(self, target_path: str) -> Dict[str, Any]:
		"""
		대상 경로의 스택을 감지

		Args:
			target_path: 대상 프로젝트 경로

		Returns:
			스택 정보 딕셔너리
		"""
		target = Path(target_path).resolve()

		if not target.exists() or not target.is_dir():
			raise ValueError(f"Invalid target path: {target_path}")

		if not self.detect_script.exists():
			raise FileNotFoundError(f"detect_stack.sh not found: {self.detect_script}")

		# detect_stack.sh 실행
		try:
			# 환경 변수를 파싱하기 위해 bash -c 사용
			cmd = f"bash -c 'source {self.detect_script} && echo \"STACK=$DETECTED_STACK\" && echo \"PM=$DETECTED_PACKAGE_MANAGER\" && echo \"VENV=$DETECTED_VENV_PATH\" && echo \"PYVER=$DETECTED_PYTHON_VERSION\"'"
			result = subprocess.run(
				cmd,
				shell=True,
				cwd=target,
				capture_output=True,
				text=True,
				timeout=30,
			)

			if result.returncode != 0:
				# 스택을 감지하지 못한 경우 (정상적인 경우일 수 있음)
				return {
					"stack": None,
					"package_manager": None,
					"venv_path": None,
					"python_version": None,
					"detected_files": [],
					"error": result.stderr or "No supported stack detected",
				}

			# 환경 변수 파싱
			output = result.stdout
			stack_match = re.search(r"STACK=(\w+)", output)
			pm_match = re.search(r"PM=(\w+)", output)
			venv_match = re.search(r"VENV=(.+)", output)
			pyver_match = re.search(r"PYVER=(.+)", output)

			stack = stack_match.group(1) if stack_match else None
			package_manager = pm_match.group(1) if pm_match else None
			venv_path = venv_match.group(1) if venv_match and venv_match.group(1) else None
			python_version = pyver_match.group(1) if pyver_match and pyver_match.group(1) else None

			# 감지된 파일 목록 수집
			detected_files = self._detect_files(target, stack)

			return {
				"stack": stack,
				"package_manager": package_manager,
				"venv_path": venv_path,
				"python_version": python_version,
				"detected_files": detected_files,
				"error": None,
			}

		except subprocess.TimeoutExpired:
			return {
				"stack": None,
				"package_manager": None,
				"venv_path": None,
				"python_version": None,
				"detected_files": [],
				"error": "Stack detection timed out",
			}
		except Exception as e:
			return {
				"stack": None,
				"package_manager": None,
				"venv_path": None,
				"python_version": None,
				"detected_files": [],
				"error": str(e),
			}

	def _detect_files(self, target: Path, stack: Optional[str]) -> List[str]:
		"""
		스택별로 감지된 파일 목록 수집

		Args:
			target: 대상 프로젝트 경로
			stack: 감지된 스택

		Returns:
			감지된 파일 목록
		"""
		files = []

		if stack == "python":
			if (target / "pyproject.toml").exists():
				files.append("pyproject.toml")
			if (target / "poetry.lock").exists():
				files.append("poetry.lock")
			if (target / "requirements.txt").exists():
				files.append("requirements.txt")
		elif stack == "node":
			if (target / "package.json").exists():
				files.append("package.json")
			if (target / "pnpm-lock.yaml").exists():
				files.append("pnpm-lock.yaml")
			elif (target / "package-lock.json").exists():
				files.append("package-lock.json")
			elif (target / "yarn.lock").exists():
				files.append("yarn.lock")
		elif stack == "go":
			if (target / "go.mod").exists():
				files.append("go.mod")
		elif stack == "rust":
			if (target / "Cargo.toml").exists():
				files.append("Cargo.toml")

		return files

