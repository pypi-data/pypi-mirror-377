"""Authentication middleware handling JWT validation and basic endpoint permissions."""

from __future__ import annotations

from typing import Awaitable, Callable

from fastapi import status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from mysingle.auth_client import (
    AuthConfig,
    AuthStrategy,
    get_unified_auth_client,
)
from mysingle.auth_utils import (
    AuthenticationError,
    extract_auth_context,
    is_public_path,
    set_auth_context,
)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT validation and basic endpoint permission checks.

    This middleware handles:
    1. JWT token validation and user context extraction
    2. Basic endpoint permission checks via IAM service
    3. Caching of permission results in Redis

    Note: Complex RBAC logic should use RBACMiddleware instead.
    """

    def __init__(
        self,
        app,
        redis: Redis | None = None,  # 호환성을 위해 유지하지만 사용하지 않음
        public_paths: list[str] | None = None,
        cache_ttl: int = 30,
    ) -> None:
        super().__init__(app)

        # 통합 권한 확인 클라이언트 사용 (IAM 우선 전략)
        auth_config = AuthConfig(
            strategy=AuthStrategy.IAM_ONLY,
            enable_cache=True,
            cache_ttl=cache_ttl,
        )
        self.auth_client = get_unified_auth_client(auth_config)

        default_public_paths = [
            "/health",
            "/version",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.public_paths = public_paths or default_public_paths

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Skip authentication for public paths
        if is_public_path(request.url.path, self.public_paths):
            return await call_next(request)

        try:
            # Extract authentication context (shared JWT processing)
            auth_context = extract_auth_context(request)
            if auth_context is None:
                return JSONResponse(
                    {"detail": "Authentication failed"},
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            set_auth_context(request, auth_context)

            # For backward compatibility, set user in request.state
            request.state.user = auth_context.payload

        except AuthenticationError as e:
            return JSONResponse(
                {"detail": e.message},
                status_code=e.status_code,
            )

        # Check endpoint-specific permissions (simple endpoint-based check)
        endpoint = None
        for route in request.app.routes:
            path = getattr(route, "path", None)
            methods = getattr(route, "methods", [])
            if path == request.url.path and request.method in methods:
                endpoint = getattr(route, "endpoint", None)
                break

        required_perm = getattr(endpoint, "required_permission", None)
        if required_perm and auth_context.token:
            if not await self._check_permission(
                auth_context.token, required_perm
            ):
                return JSONResponse(
                    {"detail": "Permission denied"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        return await call_next(request)

    async def _check_permission(self, token: str, permission: str) -> bool:
        """권한 확인 (통합 캐시 사용)"""
        # 통합 권한 확인 클라이언트 사용 (자체 캐싱 포함)
        result = await self.auth_client.check_permission(
            user_id="",  # token에서 추출됨
            resource=permission.split(":")[0]
            if ":" in permission
            else permission,
            action=permission.split(":")[-1]
            if ":" in permission
            else "access",
            token=token,
        )

        return result.allowed
