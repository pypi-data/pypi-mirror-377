"""공통 예외 처리 모듈."""

from typing import Any, Dict, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """API 에러 응답 모델."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None


class AppError(Exception):
    """공통 앱 에러 클래스."""

    def __init__(self, msg: str, *, code: str = "APP_ERROR"):
        """앱 에러 초기화."""
        super().__init__(msg)
        self.code = code


class APIError(HTTPException):
    """공통 API 에러 클래스."""

    def __init__(
        self,
        status_code: int,
        error: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """API 에러 초기화."""
        self.error = error
        self.message = message
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class ValidationError(APIError):
    """검증 에러."""

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """검증 에러 초기화."""
        super().__init__(
            status_code=422,
            error="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class NotFoundError(APIError):
    """리소스 없음 에러."""

    def __init__(self, resource: str, resource_id: str) -> None:
        """리소스 없음 에러 초기화."""
        super().__init__(
            status_code=404,
            error="NOT_FOUND",
            message=f"{resource} not found",
            details={"resource": resource, "id": resource_id},
        )


class ConflictError(APIError):
    """충돌 에러."""

    def __init__(
        self, message: str, details: Optional[Dict[str, Any]] = None
    ) -> None:
        """충돌 에러 초기화."""
        super().__init__(
            status_code=409,
            error="CONFLICT",
            message=message,
            details=details,
        )


class InternalServerError(APIError):
    """내부 서버 에러."""

    def __init__(self, message: str = "Internal server error") -> None:
        """내부 서버 에러 초기화."""
        super().__init__(
            status_code=500,
            error="INTERNAL_SERVER_ERROR",
            message=message,
        )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """API 에러 핸들러."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.error,
            message=exc.message,
            details=exc.details,
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(exclude_none=True),
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """일반 HTTP 예외 핸들러."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_EXCEPTION",
            message=exc.detail,
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(exclude_none=True),
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """일반 예외 핸들러."""
    # 실제 환경에서는 로깅 처리
    _ = exc  # 미사용 인자 처리
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="Internal server error",
            request_id=getattr(request.state, "request_id", None),
        ).model_dump(exclude_none=True),
    )


def register_exception_handlers(app: Any) -> None:
    """앱에 예외 핸들러들을 등록합니다."""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
