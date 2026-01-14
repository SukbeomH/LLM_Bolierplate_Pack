"""Inject 모듈.

보일러플레이트 주입 엔진과 관련 유틸리티.
"""

from langchain_tools.inject.injector import inject_boilerplate
from langchain_tools.inject.setup_guide import generate_setup_guide

__all__ = [
    "inject_boilerplate",
    "generate_setup_guide",
]
