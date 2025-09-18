"""통합 권한 확인 클라이언트 - IAM과 RBAC 서비스 통합"""

import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from mysingle.auth_cache import (
    AuthCacheConfig,
    UnifiedAuthCache,
    get_unified_auth_cache,
)
from mysingle.iam_client import IAMClient
from mysingle.logging import get_logger
from mysingle.rbac.rbac_client import RBACClient
from mysingle.rbac.schemas import PermissionResult

logger = get_logger(__name__)


class AuthStrategy(Enum):
    """권한 확인 전략"""

    IAM_ONLY = "iam_only"  # IAM 서비스만 사용
    RBAC_ONLY = "rbac_only"  # RBAC 서비스만 사용
    IAM_FALLBACK = "iam_fallback"  # RBAC 우선, IAM 폴백
    RBAC_FALLBACK = "rbac_fallback"  # IAM 우선, RBAC 폴백


@dataclass
class AuthConfig:
    """권한 확인 설정"""

    strategy: AuthStrategy = AuthStrategy.RBAC_FALLBACK
    enable_cache: bool = True
    cache_ttl: int = 30
    timeout: float = 5.0
    max_retries: int = 3


class UnifiedAuthClient:
    """통합 권한 확인 클라이언트

    IAM과 RBAC 서비스를 통합하여 권한 확인을 처리합니다.
    설정에 따라 다양한 전략으로 권한 확인을 수행할 수 있습니다.
    """

    def __init__(self, config: Optional[AuthConfig] = None):
        self.config = config or AuthConfig()
        self.iam_client = IAMClient()
        self.rbac_client = RBACClient(
            enable_cache=False,  # 통합 캐시를 사용하므로 개별 캐시 비활성화
            timeout=self.config.timeout,
            max_retries=self.config.max_retries,
        )

        # 통합 캐시 설정
        cache_config = AuthCacheConfig(
            local_ttl=self.config.cache_ttl,
            redis_ttl=self.config.cache_ttl * 2,  # Redis는 더 긴 TTL
        )
        self.cache: Optional[UnifiedAuthCache] = None
        self._cache_config = cache_config

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        token: Optional[str] = None,
    ) -> PermissionResult:
        """통합 권한 확인

        Args:
            user_id: 사용자 ID
            resource: 리소스 명 (예: "ledger:journals")
            action: 액션 (create|read|update|delete)
            tenant_id: 테넌트 ID (선택사항)
            context: 추가 컨텍스트 (선택사항)
            token: JWT 토큰 (IAM 확인용, 선택사항)

        Returns:
            PermissionResult: 권한 확인 결과
        """
        # 캐시 초기화 (지연 초기화)
        if self.cache is None and self.config.enable_cache:
            self.cache = await get_unified_auth_cache(self._cache_config)

        strategy = self.config.strategy
        strategy_name = strategy.value

        # 캐시에서 조회
        if self.cache:
            cached_result = await self.cache.get_permission_result(
                user_id=user_id,
                resource=resource,
                action=action,
                tenant_id=tenant_id,
                context=context,
                strategy=strategy_name,
            )
            if cached_result:
                logger.debug(f"Cache hit for {user_id}:{resource}:{action}")
                return cached_result

        # 캐시 미스 - 실제 권한 확인 수행
        try:
            result = await self._perform_permission_check(
                strategy, user_id, resource, action, tenant_id, context, token
            )

            # 결과를 캐시에 저장
            if self.cache:
                await self.cache.set_permission_result(
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    result=result,
                    tenant_id=tenant_id,
                    context=context,
                    strategy=strategy_name,
                )

            return result

        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return PermissionResult(
                allowed=False,
                reason=f"Permission check error: {str(e)}",
                cached=False,
                response_time_ms=0.0,
            )

    async def _perform_permission_check(
        self,
        strategy: AuthStrategy,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str],
        context: Optional[Dict[str, Any]],
        token: Optional[str],
    ) -> PermissionResult:
        """실제 권한 확인 수행 (캐시 없이)"""
        if strategy == AuthStrategy.IAM_ONLY:
            if not token:
                return PermissionResult(
                    allowed=False,
                    reason="Token required for IAM-only authorization",
                    cached=False,
                    response_time_ms=0.0,
                )
            return await self._check_iam_permission(
                token, f"{resource}:{action}"
            )

        elif strategy == AuthStrategy.RBAC_ONLY:
            return await self._check_rbac_permission(
                user_id, resource, action, tenant_id, context
            )

        elif strategy == AuthStrategy.IAM_FALLBACK:
            # RBAC 우선, 실패 시 IAM으로 폴백
            try:
                return await self._check_rbac_permission(
                    user_id, resource, action, tenant_id, context
                )
            except Exception as e:
                logger.warning(f"RBAC check failed, falling back to IAM: {e}")
                if token:
                    return await self._check_iam_permission(
                        token, f"{resource}:{action}"
                    )
                else:
                    return PermissionResult(
                        allowed=False,
                        reason=f"RBAC failed and no token for IAM fallback: {e}",
                        cached=False,
                        response_time_ms=0.0,
                    )

        elif strategy == AuthStrategy.RBAC_FALLBACK:
            # IAM 우선, 실패 시 RBAC로 폴백
            if token:
                try:
                    return await self._check_iam_permission(
                        token, f"{resource}:{action}"
                    )
                except Exception as e:
                    logger.warning(
                        f"IAM check failed, falling back to RBAC: {e}"
                    )
                    return await self._check_rbac_permission(
                        user_id, resource, action, tenant_id, context
                    )
            else:
                return await self._check_rbac_permission(
                    user_id, resource, action, tenant_id, context
                )
        else:
            return PermissionResult(
                allowed=False,
                reason=f"Unknown authorization strategy: {strategy}",
                cached=False,
                response_time_ms=0.0,
            )

    async def _check_iam_permission(
        self, token: str, permission: str
    ) -> PermissionResult:
        """IAM 서비스를 통한 권한 확인"""
        if not token:
            return PermissionResult(
                allowed=False,
                reason="Token required for IAM authorization",
                cached=False,
                response_time_ms=0.0,
            )

        start_time = asyncio.get_event_loop().time()
        allowed = await self.iam_client.authorize(token, permission)
        response_time = (asyncio.get_event_loop().time() - start_time) * 1000

        return PermissionResult(
            allowed=allowed,
            reason=(
                "IAM authorization check completed"
                if allowed
                else "IAM authorization denied"
            ),
            cached=False,  # IAM 자체 캐싱 사용
            response_time_ms=response_time,
        )

    async def _check_rbac_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str],
        context: Optional[Dict[str, Any]],
    ) -> PermissionResult:
        """RBAC 서비스를 통한 권한 확인"""
        return await self.rbac_client.check_permission(
            user_id=user_id,
            resource=resource,
            action=action,
            tenant_id=tenant_id,
            context=context,
        )

    async def close(self) -> None:
        """클라이언트 종료"""
        await self.iam_client.close()
        await self.rbac_client.close()


# 전역 클라이언트 인스턴스 (싱글톤 패턴)
_unified_client: Optional[UnifiedAuthClient] = None


def get_unified_auth_client(
    config: Optional[AuthConfig] = None,
) -> UnifiedAuthClient:
    """통합 권한 확인 클라이언트 싱글톤 인스턴스 반환"""
    global _unified_client
    if _unified_client is None:
        _unified_client = UnifiedAuthClient(config)
    return _unified_client


async def check_unified_permission(
    user_id: str,
    resource: str,
    action: str,
    tenant_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    token: Optional[str] = None,
    strategy: Optional[AuthStrategy] = None,
) -> PermissionResult:
    """통합 권한 확인 헬퍼 함수

    Args:
        user_id: 사용자 ID
        resource: 리소스 명
        action: 액션
        tenant_id: 테넌트 ID
        context: 추가 컨텍스트
        token: JWT 토큰
        strategy: 권한 확인 전략 (선택사항)

    Returns:
        PermissionResult: 권한 확인 결과
    """
    config = AuthConfig()
    if strategy:
        config.strategy = strategy

    client = get_unified_auth_client(config)
    return await client.check_permission(
        user_id=user_id,
        resource=resource,
        action=action,
        tenant_id=tenant_id,
        context=context,
        token=token,
    )
