from .app_factory import create_fastapi_app
from .auth_client import UnifiedAuthClient
from .base import BaseClient, BaseDoc, BaseResponseSchema
from .config import CommonSettings, settings
from .database import get_database_name, get_redis_url, init_mongo
from .exceptions import (
    APIError,
    AppError,
    ConflictError,
    ErrorResponse,
    InternalServerError,
    NotFoundError,
    ValidationError,
    api_error_handler,
    general_exception_handler,
    http_exception_handler,
    register_exception_handlers,
)
from .iam_client import IAMClient
from .logging import get_logger, setup_logging

__all__ = [
    "create_fastapi_app",
    "settings",
    "CommonSettings",
    "BaseDoc",
    "BaseClient",
    "BaseResponseSchema",
    "init_mongo",
    "get_database_name",
    "get_redis_url",
    "IAMClient",
    "UnifiedAuthClient",
    "setup_logging",
    "get_logger",
    # Exceptions
    "AppError",
    "APIError",
    "ValidationError",
    "NotFoundError",
    "ErrorResponse",
    "ConflictError",
    "InternalServerError",
    "http_exception_handler",
    "general_exception_handler",
    "register_exception_handlers",
    "api_error_handler",
]
