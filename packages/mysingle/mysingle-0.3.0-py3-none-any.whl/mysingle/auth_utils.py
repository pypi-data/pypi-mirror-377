"""Common authentication utilities for middleware."""

from typing import Any, Dict, Optional

from fastapi import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from mysingle.logging import get_logger
from mysingle.security.jwt import decode_token

logger = get_logger(__name__)


class AuthenticationContext:
    """인증 컨텍스트 클래스 - 미들웨어 간 인증 정보 공유"""

    def __init__(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        token: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        roles: Optional[list[str]] = None,
        permissions: Optional[list[str]] = None,
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.token = token
        self.payload = payload or {}
        self.roles = roles or []
        self.permissions = permissions or []


class AuthenticationError(Exception):
    """인증 관련 오류"""

    def __init__(self, message: str, status_code: int = HTTP_401_UNAUTHORIZED):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def extract_auth_context(request: Request) -> Optional[AuthenticationContext]:
    """
    요청에서 인증 컨텍스트 추출 (공통 JWT 처리 로직)

    Args:
        request: FastAPI Request 객체

    Returns:
        AuthenticationContext 또는 None

    Raises:
        AuthenticationError: 인증 실패 시
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AuthenticationError(
            "Authorization header missing or invalid format"
        )

    token = auth_header[7:]  # "Bearer " 제거

    try:
        payload = decode_token(token)
    except Exception as e:
        logger.error(f"Failed to decode JWT token: {e}")
        raise AuthenticationError("Invalid or expired token")

    # 사용자 ID 추출
    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise AuthenticationError("User ID not found in token")

    # 인증 컨텍스트 생성
    context = AuthenticationContext(
        user_id=user_id,
        tenant_id=payload.get("tenant_id"),
        token=token,
        payload=payload,
        roles=payload.get("roles", []),
        permissions=payload.get("permissions", []),
    )

    return context


def get_auth_context(request: Request) -> Optional[AuthenticationContext]:
    """
    request.state에서 인증 컨텍스트 조회

    Args:
        request: FastAPI Request 객체

    Returns:
        AuthenticationContext 또는 None
    """
    return getattr(request.state, "auth_context", None)


def set_auth_context(request: Request, context: AuthenticationContext) -> None:
    """
    request.state에 인증 컨텍스트 설정

    Args:
        request: FastAPI Request 객체
        context: 설정할 인증 컨텍스트
    """
    request.state.auth_context = context


def is_public_path(path: str, public_paths: list[str]) -> bool:
    """
    공개 경로 여부 확인

    Args:
        path: 확인할 경로
        public_paths: 공개 경로 목록

    Returns:
        bool: 공개 경로 여부
    """
    return any(path.startswith(public_path) for public_path in public_paths)
