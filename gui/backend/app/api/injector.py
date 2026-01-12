"""
Injector API 라우터

보일러플레이트 주입 관련 API 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import sys

# 프로젝트 루트를 Python 경로에 추가
backend_root = Path(__file__).parent.parent.parent
boilerplate_root = backend_root.parent.parent
sys.path.insert(0, str(backend_root))

from app.models.schemas import DetectRequest, DetectResponse, InjectRequest, InjectResponse
from app.core.detector import StackDetector

router = APIRouter(prefix="/api/v1", tags=["injector"])


@router.post("/detect", response_model=DetectResponse)
async def detect_stack(request: DetectRequest) -> DetectResponse:
	"""
	스택 감지 API

	대상 경로의 프로젝트 스택을 감지하여 반환합니다.

	Args:
		request: 스택 감지 요청 (target_path 포함)

	Returns:
		스택 감지 결과
	"""
	try:
		detector = StackDetector(boilerplate_root)
		result = detector.detect(request.target_path)

		return DetectResponse(
			stack=result.get("stack"),
			package_manager=result.get("package_manager"),
			venv_path=result.get("venv_path"),
			python_version=result.get("python_version"),
			detected_files=result.get("detected_files", []),
			error=result.get("error"),
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/inject", response_model=InjectResponse)
async def inject_boilerplate(request: InjectRequest) -> InjectResponse:
	"""
	파일 주입 API

	선택된 보일러플레이트 자산을 대상 경로로 복사합니다.

	Args:
		request: 파일 주입 요청 (target_path, assets, options 포함)

	Returns:
		파일 주입 결과
	"""
	from app.core.injector import BoilerplateInjector
	from app.core.validator import PostDiagnosisValidator
	from app.models.schemas import PostDiagnosis

	try:
		# 파일 주입 수행
		injector = BoilerplateInjector(boilerplate_root)
		inject_result = injector.inject(
			target_path=request.target_path,
			assets=request.assets,
			options=request.options,
		)

		# 사후 진단 수행
		validator = PostDiagnosisValidator(boilerplate_root)
		diagnosis_result = validator.validate(request.target_path)

		return InjectResponse(
			status=inject_result.get("status", "success"),
			injected_files=inject_result.get("injected_files", []),
			backed_up_files=inject_result.get("backed_up_files", []),
			skipped_files=inject_result.get("skipped_files", []),
			merged_files=inject_result.get("merged_files", []),
			post_diagnosis=PostDiagnosis(
				env_check=diagnosis_result.get("env_check"),
				git_status=diagnosis_result.get("git_status"),
			),
			error=inject_result.get("error"),
		)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

