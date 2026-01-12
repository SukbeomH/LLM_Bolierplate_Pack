"""
백업 관리 로직

기존 파일을 백업하고 복원하는 기능을 제공합니다.
"""

import shutil
from pathlib import Path
from typing import Optional


class BackupManager:
	"""백업 관리 클래스"""

	@staticmethod
	def create_backup(file_path: Path) -> Optional[Path]:
		"""
		파일 백업 생성

		Args:
			file_path: 백업할 파일 경로

		Returns:
			백업 파일 경로 (실패 시 None)
		"""
		if not file_path.exists():
			return None

		backup_path = file_path.with_suffix(file_path.suffix + ".bak")

		try:
			if file_path.is_file():
				shutil.copy2(file_path, backup_path)
			elif file_path.is_dir():
				# 디렉토리의 경우 .bak 확장자를 이름에 추가
				backup_path = file_path.parent / f"{file_path.name}.bak"
				if backup_path.exists():
					shutil.rmtree(backup_path)
				shutil.copytree(file_path, backup_path)
			return backup_path
		except Exception:
			return None

	@staticmethod
	def restore_backup(backup_path: Path, target_path: Path) -> bool:
		"""
		백업 파일 복원

		Args:
			backup_path: 백업 파일 경로
			target_path: 복원할 대상 경로

		Returns:
			복원 성공 여부
		"""
		if not backup_path.exists():
			return False

		try:
			if backup_path.is_file():
				shutil.copy2(backup_path, target_path)
			elif backup_path.is_dir():
				if target_path.exists():
					shutil.rmtree(target_path)
				shutil.copytree(backup_path, target_path)
			return True
		except Exception:
			return False

