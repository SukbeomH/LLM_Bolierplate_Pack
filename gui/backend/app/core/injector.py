"""
파일 주입 로직

보일러플레이트 자산을 대상 프로젝트로 복사합니다.
"""

import shutil
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator
from app.core.backup import BackupManager
from app.models.schemas import InjectionOptions


class BoilerplateInjector:
	"""보일러플레이트 주입 클래스"""

	# 주입 가능한 자산 목록 및 소스 경로
	ASSETS_MAP = {
		".claude/": ".claude/",
		"scripts/": "scripts/",
		"CLAUDE.md": "CLAUDE.md",
		"mise.toml": "mise.toml",
		".mcp.json": ".mcp.json",
		"docs/ai-onboarding.md": "docs/ai-onboarding.md",
		"logging.conf": "logging.conf",
		"zmp-branch-policy.json": "zmp-branch-policy.json",
		".pre-commit-config.yaml": ".pre-commit-config.yaml",
		".github/workflows/": ".github/workflows/",
		"docker-compose.yml": "docker-compose.yml",
		".gitignore": ".gitignore",
	}

	def __init__(self, boilerplate_root: Path):
		"""
		초기화

		Args:
			boilerplate_root: 보일러플레이트 프로젝트 루트 경로
		"""
		self.boilerplate_root = boilerplate_root
		self.backup_manager = BackupManager()

	def inject(
		self,
		target_path: str,
		assets: List[str],
		options: InjectionOptions,
	) -> Dict[str, Any]:
		"""
		보일러플레이트 자산 주입

		Args:
			target_path: 대상 프로젝트 경로
			assets: 주입할 자산 목록
			options: 주입 옵션

		Returns:
			주입 결과 딕셔너리
		"""
		target = Path(target_path).resolve()
		injected_files = []
		backed_up_files = []
		skipped_files = []
		merged_files = []

		try:
			for asset in assets:
				if asset not in self.ASSETS_MAP:
					continue

				source_path = self.boilerplate_root / self.ASSETS_MAP[asset]
				target_asset_path = target / asset.rstrip("/")

				# 소스 파일이 존재하는지 확인
				if not source_path.exists():
					skipped_files.append(asset)
					continue

				# 대상 경로에 이미 존재하는 경우
				if target_asset_path.exists():
					if options.skip_existing:
						skipped_files.append(asset)
						continue

					if options.backup_existing:
						backup_path = self.backup_manager.create_backup(target_asset_path)
						if backup_path:
							backed_up_files.append(str(backup_path.relative_to(target)))

					# .claude/ 설정 병합
					if asset == ".claude/" and options.merge_claude_config:
						if self._merge_claude_config(source_path, target_asset_path):
							merged_files.append(asset)
							continue

				# scripts/ 주입 시 boilerplate/ 디렉토리로 복사하고 gui/도 boilerplate/gui/로 복사
				if asset == "scripts/":
					# scripts/를 boilerplate/로 복사
					boilerplate_target = target / "boilerplate"
					if self._copy_asset(source_path, boilerplate_target):
						# gui/ 디렉토리를 boilerplate/gui/로 복사
						gui_source = self.boilerplate_root / "gui"
						gui_target = boilerplate_target / "gui"
						if gui_source.exists() and gui_source.is_dir():
							# boilerplate/gui/ 디렉토리 생성
							gui_target.mkdir(parents=True, exist_ok=True)

							# boilerplate/gui/start.sh는 이미 있으므로 backend와 frontend만 복사
							if (gui_source / "backend").exists():
								backend_target = gui_target / "backend"
								# 기존 파일 처리 (백업 옵션 확인)
								if backend_target.exists():
									if options.skip_existing:
										skipped_files.append("boilerplate/gui/backend")
									else:
										if options.backup_existing:
											backup_path = self.backup_manager.create_backup(backend_target)
											if backup_path:
												backed_up_files.append(str(backup_path.relative_to(target)))
										if self._copy_asset(gui_source / "backend", backend_target):
											injected_files.append("boilerplate/gui/backend")
								else:
									if self._copy_asset(gui_source / "backend", backend_target):
										injected_files.append("boilerplate/gui/backend")

							if (gui_source / "frontend").exists():
								frontend_target = gui_target / "frontend"
								# 기존 파일 처리 (백업 옵션 확인)
								if frontend_target.exists():
									if options.skip_existing:
										skipped_files.append("boilerplate/gui/frontend")
									else:
										if options.backup_existing:
											backup_path = self.backup_manager.create_backup(frontend_target)
											if backup_path:
												backed_up_files.append(str(backup_path.relative_to(target)))
										if self._copy_asset(gui_source / "frontend", frontend_target):
											injected_files.append("boilerplate/gui/frontend")
								else:
									if self._copy_asset(gui_source / "frontend", frontend_target):
										injected_files.append("boilerplate/gui/frontend")

							# Dockerfile 복사 (backend와 frontend가 성공적으로 복사된 경우)
							if (gui_target / "backend").exists() and (gui_source / "backend" / "Dockerfile").exists():
								dockerfile_backend_source = gui_source / "backend" / "Dockerfile"
								dockerfile_backend_target = gui_target / "backend" / "Dockerfile"
								if not dockerfile_backend_target.exists() or not options.skip_existing:
									if dockerfile_backend_target.exists() and options.backup_existing:
										backup_path = self.backup_manager.create_backup(dockerfile_backend_target)
										if backup_path:
											backed_up_files.append(str(backup_path.relative_to(target)))
									if self._copy_asset(dockerfile_backend_source, dockerfile_backend_target):
										injected_files.append("boilerplate/gui/backend/Dockerfile")

							if (gui_target / "frontend").exists() and (gui_source / "frontend" / "Dockerfile").exists():
								dockerfile_frontend_source = gui_source / "frontend" / "Dockerfile"
								dockerfile_frontend_target = gui_target / "frontend" / "Dockerfile"
								if not dockerfile_frontend_target.exists() or not options.skip_existing:
									if dockerfile_frontend_target.exists() and options.backup_existing:
										backup_path = self.backup_manager.create_backup(dockerfile_frontend_target)
										if backup_path:
											backed_up_files.append(str(backup_path.relative_to(target)))
									if self._copy_asset(dockerfile_frontend_source, dockerfile_frontend_target):
										injected_files.append("boilerplate/gui/frontend/Dockerfile")
						injected_files.append("boilerplate/")
					else:
						skipped_files.append(asset)
				# docker-compose.yml 주입 시 boilerplate/ 경로로 복사 및 경로 수정
				elif asset == "docker-compose.yml":
					# boilerplate/docker-compose.yml로 복사
					target_docker_compose = target / "boilerplate" / "docker-compose.yml"
					success, backup_path = self._inject_docker_compose(source_path, target_docker_compose, target, options)
					if success:
						injected_files.append("boilerplate/docker-compose.yml")
						if backup_path:
							backed_up_files.append(str(backup_path.relative_to(target)))
					else:
						skipped_files.append(asset)
				# .gitignore 주입 시 boilerplate/.gitignore로 복사 및 병합
				elif asset == ".gitignore":
					# boilerplate/.gitignore로 복사
					target_gitignore = target / "boilerplate" / ".gitignore"
					success, backup_path = self._inject_gitignore(source_path, target_gitignore, target, options)
					if success:
						injected_files.append("boilerplate/.gitignore")
						if backup_path:
							backed_up_files.append(str(backup_path.relative_to(target)))
					else:
						skipped_files.append(asset)
				# 파일/디렉토리 복사
				elif self._copy_asset(source_path, target_asset_path):
					injected_files.append(asset)
				else:
					skipped_files.append(asset)

			return {
				"status": "success" if injected_files else "partial",
				"injected_files": injected_files,
				"backed_up_files": backed_up_files,
				"skipped_files": skipped_files,
				"merged_files": merged_files,
			}

		except Exception as e:
			return {
				"status": "error",
				"injected_files": injected_files,
				"backed_up_files": backed_up_files,
				"skipped_files": skipped_files,
				"merged_files": merged_files,
				"error": str(e),
			}

	def _copy_asset(self, source: Path, target: Path) -> bool:
		"""
		자산 복사

		Args:
			source: 소스 경로
			target: 대상 경로

		Returns:
			복사 성공 여부
		"""
		try:
			# 대상 디렉토리 생성
			target.parent.mkdir(parents=True, exist_ok=True)

			if source.is_file():
				shutil.copy2(source, target)
			elif source.is_dir():
				if target.exists():
					shutil.rmtree(target)
				shutil.copytree(source, target, dirs_exist_ok=True)

			return True
		except Exception as e:
			print(f"Error copying {source} to {target}: {e}")
			return False

	def _merge_claude_config(self, source_claude: Path, target_claude: Path) -> bool:
		"""
		.claude/ 설정 병합

		Args:
			source_claude: 소스 .claude/ 디렉토리
			target_claude: 대상 .claude/ 디렉토리

		Returns:
			병합 성공 여부
		"""
		try:
			source_settings = source_claude / "settings.json"
			target_settings = target_claude / "settings.json"

			if not source_settings.exists():
				return False

			# 기존 설정이 없으면 그냥 복사
			if not target_settings.exists():
				shutil.copy2(source_settings, target_settings)
				return True

			# 기존 설정 로드
			with open(target_settings, "r", encoding="utf-8") as f:
				target_config = json.load(f)

			with open(source_settings, "r", encoding="utf-8") as f:
				source_config = json.load(f)

			# JSON 구조 검증
			if not isinstance(target_config, dict):
				raise ValueError("Target config is not a valid JSON object")
			if not isinstance(source_config, dict):
				raise ValueError("Source config is not a valid JSON object")

			# 설정 병합
			merged_config = self._merge_json_config(target_config, source_config)

			# 병합된 설정 저장
			with open(target_settings, "w", encoding="utf-8") as f:
				json.dump(merged_config, f, indent=2, ensure_ascii=False)

			return True

		except Exception as e:
			print(f"Error merging .claude config: {e}")
			return False

	def _inject_docker_compose(
		self, source: Path, target: Path, target_project: Path, options: InjectionOptions
	) -> tuple[bool, Optional[Path]]:
		"""
		docker-compose.yml 주입 (경로 수정)

		Args:
			source: 소스 docker-compose.yml 경로
			target: 대상 docker-compose.yml 경로
			target_project: 대상 프로젝트 루트 경로
			options: 주입 옵션

		Returns:
			(주입 성공 여부, 백업 경로)
		"""
		try:
			if not source.exists():
				return False, None

			backup_path = None
			# 기존 파일 처리
			if target.exists():
				if options.skip_existing:
					return False, None
				if options.backup_existing:
					backup_path = self.backup_manager.create_backup(target)

			# docker-compose.yml 읽기
			with open(source, "r", encoding="utf-8") as f:
				content = f.read()

			# 경로 수정
			# docker-compose.yml이 boilerplate/에 있으므로 상대 경로는 그대로 유지
			# boilerplate/docker-compose.yml에서 boilerplate/gui/backend를 참조하려면 ./gui/backend
			# (boilerplate/ 디렉토리에서 상대 경로로 ./gui/backend는 boilerplate/gui/backend를 가리킴)
			# 컨테이너 이름도 프로젝트별로 변경
			project_name = target_project.name.lower().replace(" ", "-").replace("_", "-")

			# 경로는 이미 ./gui/backend 형식이므로 그대로 유지 (boilerplate/에서 실행 시 올바른 경로)
			# 컨테이너 이름만 변경
			content = content.replace("boilerplate-backend", f"{project_name}-backend")
			content = content.replace("boilerplate-frontend", f"{project_name}-frontend")

			# 주석 업데이트: boilerplate/ 경로에 맞게 수정
			content = content.replace(
				"#   docker-compose up -d",
				"#   cd boilerplate && docker-compose -f docker-compose.yml up -d"
			)

			# 대상 디렉토리 생성
			target.parent.mkdir(parents=True, exist_ok=True)

			# 수정된 내용 저장
			with open(target, "w", encoding="utf-8") as f:
				f.write(content)

			return True, backup_path
		except Exception as e:
			print(f"Error injecting docker-compose.yml: {e}")
			return False, None

	def _inject_gitignore(
		self, source: Path, target: Path, target_project: Path, options: InjectionOptions
	) -> tuple[bool, Optional[Path]]:
		"""
		.gitignore 주입 (boilerplate/.gitignore로 복사)

		Args:
			source: 소스 .gitignore 경로
			target: 대상 .gitignore 경로 (boilerplate/.gitignore)
			target_project: 대상 프로젝트 루트 경로
			options: 주입 옵션

		Returns:
			(주입 성공 여부, 백업 경로)
		"""
		try:
			if not source.exists():
				return False, None

			backup_path = None
			# 기존 파일 처리
			if target.exists():
				if options.skip_existing:
					return False, None
				if options.backup_existing:
					backup_path = self.backup_manager.create_backup(target)

			# 대상 디렉토리 생성
			target.parent.mkdir(parents=True, exist_ok=True)

			# .gitignore 복사
			shutil.copy2(source, target)

			return True, backup_path
		except Exception as e:
			print(f"Error injecting .gitignore: {e}")
			return False, None

	def _merge_json_config(self, target: Dict, source: Dict) -> Dict:
		"""
		JSON 설정 병합

		Args:
			target: 기존 설정
			source: 새 설정

		Returns:
			병합된 설정
		"""
		merged = target.copy()

		# permissions: 합집합 (중복 제거)
		if "permissions" in source:
			target_perms_list = target.get("permissions", [])
			source_perms_list = source.get("permissions", [])

			# 리스트 타입 검증
			if not isinstance(target_perms_list, list):
				target_perms_list = []
			if not isinstance(source_perms_list, list):
				source_perms_list = []

			# 모든 항목이 문자열인지 확인
			target_perms = set(p for p in target_perms_list if isinstance(p, str))
			source_perms = set(p for p in source_perms_list if isinstance(p, str))
			merged["permissions"] = sorted(list(target_perms | source_perms))

		# hooks: 새 설정 우선 (기존 설정 백업 후)
		if "hooks" in source:
			merged["hooks"] = source["hooks"]

		# 기타 설정: 새 설정으로 덮어쓰기 (단, 기존 설정이 없을 때만)
		for key, value in source.items():
			if key not in merged:
				merged[key] = value

		return merged

	def _post_process_python(self, target: Path) -> Dict[str, Any]:
		"""
		Python 프로젝트 후처리: Poetry 프로젝트를 uv로 마이그레이션

		Args:
			target: 대상 프로젝트 경로

		Returns:
			후처리 결과 딕셔너리
		"""
		result = {
			"executed": False,
			"success": False,
			"message": "",
			"migration": False,
		}

		# Python 프로젝트인지 확인 (pyproject.toml 존재)
		pyproject_toml = target / "pyproject.toml"
		poetry_lock = target / "poetry.lock"

		if not pyproject_toml.exists():
			result["message"] = "Not a Python project, skipping post-process"
			return result

		# poetry.lock이 있으면 uv 마이그레이션 실행
		if poetry_lock.exists():
			try:
				import subprocess

				# migrate_to_uv.sh 실행
				migrate_script = self.boilerplate_root / "scripts" / "core" / "migrate_to_uv.sh"
				if not migrate_script.exists():
					result["message"] = "migrate_to_uv.sh not found"
					return result

				result["executed"] = True
				result["migration"] = True

				# 마이그레이션 스크립트 실행
				migrate_result = subprocess.run(
					["bash", str(migrate_script), str(target)],
					cwd=target,
					capture_output=True,
					text=True,
					timeout=300,  # 5분 타임아웃
				)

				if migrate_result.returncode == 0:
					result["success"] = True
					result["message"] = "Successfully migrated from Poetry to uv"
					if migrate_result.stdout:
						result["message"] += f"\n{migrate_result.stdout[-500:]}"  # 마지막 500자만
				else:
					result["success"] = False
					result["message"] = f"Migration failed: {migrate_result.stderr[-500:] if migrate_result.stderr else 'Unknown error'}"

			except subprocess.TimeoutExpired:
				result["executed"] = True
				result["success"] = False
				result["message"] = "Migration timed out (exceeded 5 minutes)"
			except FileNotFoundError:
				result["executed"] = False
				result["message"] = "bash or migrate_to_uv.sh not found"
			except Exception as e:
				result["executed"] = True
				result["success"] = False
				result["message"] = f"Unexpected error during migration: {str(e)}"
		else:
			# poetry.lock이 없으면 단순히 uv 프로젝트로 확인
			result["message"] = "Not a Poetry project (no poetry.lock), skipping migration"

		return result

