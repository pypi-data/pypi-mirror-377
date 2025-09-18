"""RBAC 권한 확인 미들웨어 - 고급 권한 관리 전용"""

import json
import time
from typing import Any, Callable, Dict, List, Optional, Set

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

from mysingle.auth_utils import (
    AuthenticationError,
    extract_auth_context,
    get_auth_context,
    set_auth_context,
)

# 순환 import 방지를 위해 직접 import
from mysingle.logging import get_logger
from mysingle.rbac.exceptions import PermissionDeniedError, RBACError
from mysingle.rbac.rbac_client import get_rbac_client

logger = get_logger(__name__)


class RBACMiddleware(BaseHTTPMiddleware):
    """고급 RBAC 권한 확인 미들웨어

    이 미들웨어는 복잡한 권한 관리가 필요한 경우에만 사용합니다:
    - 경로 기반 자동 권한 매핑
    - 테넌트별 권한 확인
    - 배치 권한 확인 최적화

    주의: AuthMiddleware와 함께 사용 시 AuthMiddleware가 먼저 적용되어야 합니다.
    """

    def __init__(
        self,
        app,
        rbac_service_url: Optional[str] = None,
        protected_paths: Optional[Dict[str, Dict[str, str]]] = None,
        excluded_paths: Optional[Set[str]] = None,
        enable_path_based_check: bool = False,
        enable_batch_optimization: bool = True,
    ):
        """
        RBAC 미들웨어 초기화

        Args:
            app: FastAPI 애플리케이션
            rbac_service_url: RBAC 서비스 URL
            protected_paths: 보호할 경로와 권한 매핑
                {"/api/v1/ledger/journals": {"resource": "ledger:journals", "action": "read"}}
            excluded_paths: 권한 확인에서 제외할 경로들
            enable_path_based_check: 경로 기반 자동 권한 확인 활성화
            enable_batch_optimization: 배치 권한 확인 최적화 활성화
        """
        super().__init__(app)
        self.rbac_service_url = rbac_service_url
        self.protected_paths = protected_paths or {}
        self.excluded_paths = excluded_paths or {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
        }
        self.enable_path_based_check = enable_path_based_check
        self.enable_batch_optimization = enable_batch_optimization

        # HTTP 메서드에서 RBAC 액션으로 매핑
        self.method_to_action = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """미들웨어 메인 로직"""
        start_time = time.time()

        # 제외 경로 확인
        if self._is_excluded_path(request.url.path):
            response = await call_next(request)
            return response  # type: ignore[no-any-return]

        try:
            # 권한 확인이 필요한지 판단
            if not self._needs_permission_check(request):
                response = await call_next(request)
                return response  # type: ignore[no-any-return]

            # 사용자 인증 정보 추출
            user_info = await self._extract_user_info(request)
            if not user_info:
                return self._create_error_response(
                    401, "Authentication required"
                )

            # 권한 확인
            if self.enable_path_based_check:
                permission_result = await self._check_path_based_permission(
                    request, user_info
                )
                if not permission_result:
                    return self._create_error_response(
                        HTTP_403_FORBIDDEN,
                        "Insufficient privileges for this operation",
                    )

                # 권한 정보를 request.state에 저장
                request.state.rbac_info = permission_result
                request.state.user_info = user_info

            # 다음 미들웨어/핸들러 실행
            response = await call_next(request)

            # 응답 시간 로깅
            response_time = (time.time() - start_time) * 1000
            logger.debug(
                f"RBAC middleware: {request.method} {request.url.path} - {response_time:.2f}ms"
            )

            return response  # type: ignore[no-any-return]

        except PermissionDeniedError as e:
            logger.warning(f"Permission denied: {e.message}")
            return self._create_error_response(HTTP_403_FORBIDDEN, e.message)

        except RBACError as e:
            logger.error(f"RBAC error: {e.message}")
            return self._create_error_response(
                HTTP_500_INTERNAL_SERVER_ERROR, "Permission check failed"
            )

        except Exception as e:
            logger.error(f"Unexpected error in RBAC middleware: {e}")
            return self._create_error_response(
                HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error"
            )

    def _is_excluded_path(self, path: str) -> bool:
        """제외 경로인지 확인"""
        return any(
            path.startswith(excluded) for excluded in self.excluded_paths
        )

    def _needs_permission_check(self, request: Request) -> bool:
        """권한 확인이 필요한지 판단"""
        # OPTIONS 요청은 제외
        if request.method == "OPTIONS":
            return False

        # 경로 기반 확인이 활성화되어 있고 보호된 경로인 경우
        if self.enable_path_based_check:
            return self._is_protected_path(request.url.path)

        # 기본적으로는 데코레이터에서 처리하므로 false
        return False

    def _is_protected_path(self, path: str) -> bool:
        """보호된 경로인지 확인"""
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        return False

    async def _extract_user_info(
        self, request: Request
    ) -> Optional[Dict[str, Any]]:
        """요청에서 사용자 정보 추출 (공통 인증 유틸리티 사용)"""
        # 이미 AuthMiddleware에서 처리된 인증 컨텍스트가 있는지 확인
        auth_context = get_auth_context(request)
        if auth_context:
            return {
                "user_id": auth_context.user_id,
                "tenant_id": auth_context.tenant_id,
                "roles": auth_context.roles,
                "permissions": auth_context.permissions,
            }

        # AuthMiddleware가 없는 경우 직접 인증 처리
        try:
            auth_context = extract_auth_context(request)
            if auth_context is None:
                return None

            # 인증 컨텍스트를 request.state에 저장
            set_auth_context(request, auth_context)

            return {
                "user_id": auth_context.user_id,
                "tenant_id": auth_context.tenant_id,
                "roles": auth_context.roles,
                "permissions": auth_context.permissions,
            }
        except AuthenticationError as e:
            logger.error(f"Failed to extract user info: {e.message}")
            return None

    async def _check_path_based_permission(
        self, request: Request, user_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """경로 기반 권한 확인"""
        # 경로에 매핑된 권한 정보 조회
        permission_config = self._get_path_permission_config(request.url.path)
        if not permission_config:
            # 자동 매핑: /api/v1/ledger/journals -> ledger:journals
            permission_config = self._auto_generate_permission_config(request)

        if not permission_config:
            return None

        # 테넌트 ID 추출
        tenant_id = self._extract_tenant_id(request, user_info)

        # RBAC 클라이언트를 통한 권한 확인
        try:
            client = await get_rbac_client(self.rbac_service_url)
            result = await client.check_permission(
                user_id=user_info["user_id"],
                resource=permission_config["resource"],
                action=permission_config["action"],
                tenant_id=tenant_id,
                context={"path": request.url.path, "method": request.method},
            )

            if result.allowed:
                return {
                    "permission_config": permission_config,
                    "result": result.model_dump(),
                    "tenant_id": tenant_id,
                }
            else:
                logger.warning(
                    f"Permission denied via middleware: user={user_info['user_id']}, "
                    f"resource={permission_config['resource']}, action={permission_config['action']}, "
                    f"reason={result.reason}"
                )
                return None

        except Exception as e:
            logger.error(f"Error checking permission via middleware: {e}")
            return None

    def _get_path_permission_config(
        self, path: str
    ) -> Optional[Dict[str, str]]:
        """경로에 대한 권한 설정 조회"""
        for protected_path, config in self.protected_paths.items():
            if path.startswith(protected_path):
                return config
        return None

    def _auto_generate_permission_config(
        self, request: Request
    ) -> Optional[Dict[str, str]]:
        """경로에서 자동으로 권한 설정 생성"""
        path = request.url.path
        method = request.method

        # /api/v1/{service}/{resource} 패턴 매칭
        path_parts = path.strip("/").split("/")
        if (
            len(path_parts) >= 3
            and path_parts[0] == "api"
            and path_parts[1] == "v1"
        ):
            service = path_parts[2]
            resource = path_parts[3] if len(path_parts) > 3 else service

            # HTTP 메서드를 RBAC 액션으로 변환
            action = self.method_to_action.get(method, "read")

            return {"resource": f"{service}:{resource}", "action": action}

        return None

    def _extract_tenant_id(
        self, request: Request, user_info: Dict[str, Any]
    ) -> Optional[str]:
        """요청에서 테넌트 ID 추출"""
        # 1. 경로 매개변수에서 확인
        if "tenant_id" in request.path_params:
            tenant_id = request.path_params["tenant_id"]
            return str(tenant_id) if tenant_id is not None else None

        # 2. 쿼리 매개변수에서 확인
        if "tenant_id" in request.query_params:
            tenant_id = request.query_params["tenant_id"]
            return str(tenant_id) if tenant_id is not None else None

        # 3. JWT 토큰에서 확인
        tenant_id = user_info.get("tenant_id")
        return str(tenant_id) if tenant_id is not None else None

    def _create_error_response(
        self, status_code: int, message: str
    ) -> Response:
        """오류 응답 생성"""
        content = {
            "error": True,
            "message": message,
            "status_code": status_code,
        }

        return Response(
            content=json.dumps(content),
            status_code=status_code,
            media_type="application/json",
        )


class RBACMiddlewareConfig:
    """RBAC 미들웨어 설정 헬퍼"""

    @staticmethod
    def create_default_config() -> Dict[str, Any]:
        """기본 RBAC 미들웨어 설정 생성"""
        return {
            "enable_path_based_check": True,
            "enable_batch_optimization": True,
            "excluded_paths": {
                "/health",
                "/docs",
                "/redoc",
                "/openapi.json",
                "/api/v1/auth/login",
                "/api/v1/auth/refresh",
                "/api/v1/iam/auth/",
                "/metrics",
            },
            "protected_paths": {
                # Ledger Service
                "/api/v1/ledger/journals": {
                    "resource": "ledger:journals",
                    "action": "read",
                },
                "/api/v1/ledger/accounts": {
                    "resource": "ledger:accounts",
                    "action": "read",
                },
                "/api/v1/ledger/reports": {
                    "resource": "ledger:reports",
                    "action": "read",
                },
                # Tenant Service
                "/api/v1/tenant/subscriptions": {
                    "resource": "tenant:subscriptions",
                    "action": "read",
                },
                "/api/v1/tenant/members": {
                    "resource": "tenant:members",
                    "action": "read",
                },
                "/api/v1/tenant/roles": {
                    "resource": "tenant:roles",
                    "action": "read",
                },
                # CRM Service (향후)
                "/api/v1/crm/contacts": {
                    "resource": "crm:contacts",
                    "action": "read",
                },
                "/api/v1/crm/deals": {
                    "resource": "crm:deals",
                    "action": "read",
                },
                # Asset Service (향후)
                "/api/v1/asset/equipment": {
                    "resource": "asset:equipment",
                    "action": "read",
                },
            },
        }

    @staticmethod
    def create_service_config(
        service_name: str, resources: List[str]
    ) -> Dict[str, Dict[str, str]]:
        """서비스별 보호 경로 설정 생성"""
        protected_paths = {}

        for resource in resources:
            base_path = f"/api/v1/{service_name}/{resource}"
            protected_paths[base_path] = {
                "resource": f"{service_name}:{resource}",
                "action": "read",  # 기본값, 실제로는 메서드별로 다름
            }

        return protected_paths
