"""RBAC 서비스 클라이언트"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx

from mysingle.config import settings
from mysingle.logging import get_logger
from mysingle.rbac.cache import RBACCache
from mysingle.rbac.exceptions import (
    PermissionDeniedError,
    RBACError,
    RBACServiceUnavailableError,
    RBACTimeoutError,
)

from ..rbac.schemas import (
    BatchPermissionRequest,
    PermissionRequest,
    PermissionResult,
)

logger = get_logger(__name__)


class RBACClient:
    """RBAC 서비스 클라이언트"""

    def __init__(
        self,
        rbac_service_url: str = settings.RBAC_SERVICE_URL,
        timeout: float = 5.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_cache: bool = True,
        cache_config: Optional[Dict[str, Any]] = None,
    ):
        self.rbac_url = rbac_service_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_cache = enable_cache

        # HTTP 클라이언트 설정
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(
                max_connections=20, max_keepalive_connections=5
            ),
        )

        # 캐시 설정
        self.cache: Optional[RBACCache]
        if enable_cache:
            cache_config = cache_config or {}
            self.cache = RBACCache(**cache_config)
        else:
            self.cache = None

        self._initialized = False

    async def initialize(self) -> None:
        """클라이언트 초기화"""
        if self.cache:
            await self.cache.initialize()
        self._initialized = True
        logger.info(f"RBAC client initialized for service: {self.rbac_url}")

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> PermissionResult:
        """단일 권한 확인"""
        start_time = time.time()

        # 캐시 확인
        cache_key = None
        if self.enable_cache and use_cache and self.cache:
            cache_key = RBACCache.generate_cache_key(
                user_id, resource, action, tenant_id, context
            )
            cached_result = await self.cache.get_permission(cache_key)
            if cached_result:
                cached_permission = PermissionResult(**cached_result)
                cached_permission.cached = True
                cached_permission.response_time_ms = (
                    time.time() - start_time
                ) * 1000
                logger.debug(
                    f"Permission check (cached): {user_id} {resource}:{action} = {cached_permission.allowed}"
                )
                return cached_permission

        # RBAC 서비스 호출
        request = PermissionRequest(
            user_id=user_id,
            resource=resource,
            action=action,
            tenant_id=tenant_id,
            context=context,
        )

        service_result = await self._call_rbac_service(
            "/api/v1/decisions/check", request.model_dump()
        )
        permission_result = PermissionResult(**service_result)
        permission_result.response_time_ms = (time.time() - start_time) * 1000

        # 캐시에 저장
        if self.enable_cache and self.cache and cache_key:
            await self.cache.set_permission(
                cache_key, permission_result.model_dump()
            )

        logger.debug(
            f"Permission check: {user_id} {resource}:{action} = {permission_result.allowed}"
        )
        return permission_result

    async def batch_check_permissions(
        self,
        user_id: str,
        permissions: List[Dict[str, str]],
        tenant_id: Optional[str] = None,
    ) -> Dict[str, PermissionResult]:
        """배치 권한 확인"""
        start_time = time.time()

        request = BatchPermissionRequest(
            user_id=user_id, tenant_id=tenant_id, permissions=permissions
        )

        result = await self._call_rbac_service(
            "/api/v1/decisions/batch-check", request.model_dump()
        )

        # 결과 변환
        batch_results = {}
        for key, permission_data in result.get("results", {}).items():
            batch_results[key] = PermissionResult(**permission_data)

        response_time = (time.time() - start_time) * 1000
        logger.debug(
            f"Batch permission check: {user_id} ({len(permissions)} permissions) in {response_time:.2f}ms"
        )

        return batch_results

    async def get_user_permissions(
        self, user_id: str, tenant_id: Optional[str] = None
    ) -> List[str]:
        """사용자 권한 목록 조회"""
        request_data = {"user_id": user_id}
        if tenant_id:
            request_data["tenant_id"] = tenant_id

        result = await self._call_rbac_service(
            "/api/v1/decisions/user-permissions", request_data
        )
        permissions = result.get("permissions", [])
        if isinstance(permissions, list):
            return permissions
        return []

    async def invalidate_user_cache(
        self, user_id: str, tenant_id: Optional[str] = None
    ) -> None:
        """사용자 권한 캐시 무효화"""
        if self.cache:
            await self.cache.invalidate_user_permissions(user_id, tenant_id)

    async def health_check(self) -> bool:
        """RBAC 서비스 헬스체크"""
        try:
            response = await self._client.get(f"{self.rbac_url}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"RBAC service health check failed: {e}")
            return False

    async def _call_rbac_service(
        self, endpoint: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """RBAC 서비스 API 호출"""
        url = urljoin(f"{self.rbac_url}/", endpoint.lstrip("/"))

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.post(url, json=data)

                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, dict):
                        return result
                    raise RBACError(f"Invalid response format: {type(result)}")
                elif response.status_code == 403:
                    # 권한 거부는 재시도하지 않음
                    error_detail = response.json().get(
                        "detail", "Permission denied"
                    )
                    raise PermissionDeniedError(
                        data.get("user_id", "unknown"),
                        data.get("resource", "unknown"),
                        data.get("action", "unknown"),
                        error_detail,
                    )
                else:
                    raise RBACServiceUnavailableError(
                        self.rbac_url,
                        f"HTTP {response.status_code}: {response.text}",
                    )

            except httpx.TimeoutException:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise RBACTimeoutError(self.timeout, f"POST {endpoint}")

            except httpx.RequestError as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise RBACServiceUnavailableError(self.rbac_url, str(e))

            except (PermissionDeniedError, RBACTimeoutError):
                # 이미 특정 예외로 처리된 경우 재시도하지 않음
                raise

            except Exception as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                raise RBACError(f"Unexpected error calling RBAC service: {e}")

        raise RBACServiceUnavailableError(
            self.rbac_url, "Max retries exceeded"
        )

    async def close(self) -> None:
        """클라이언트 리소스 정리"""
        await self._client.aclose()
        if self.cache:
            await self.cache.close()
        logger.info("RBAC client closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        asyncio.create_task(self.close())

    async def __aenter__(self):
        if not self._initialized:
            await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 전역 RBAC 클라이언트 인스턴스 (싱글톤)
_global_rbac_client: Optional[RBACClient] = None


async def get_rbac_client(
    rbac_service_url: Optional[str] = None, **kwargs
) -> RBACClient:
    """전역 RBAC 클라이언트 조회/생성"""
    global _global_rbac_client

    if _global_rbac_client is None:
        if rbac_service_url is None:
            # 환경변수 또는 기본값 사용
            import os

            rbac_service_url = os.getenv(
                "RBAC_SERVICE_URL", "http://localhost:8000"
            )

        _global_rbac_client = RBACClient(rbac_service_url, **kwargs)
        await _global_rbac_client.initialize()

    return _global_rbac_client


async def close_global_rbac_client() -> None:
    """전역 RBAC 클라이언트 종료"""
    global _global_rbac_client

    if _global_rbac_client:
        await _global_rbac_client.close()
        _global_rbac_client = None
