"""권한 확인 로직"""

from typing import Any, Dict, Optional

from mysingle.auth_client import AuthConfig, UnifiedAuthClient
from mysingle.logging import get_logger

from ..core.base import IPermissionChecker
from ..core.config import GuardrailConfig

logger = get_logger(__name__)


class PermissionChecker(IPermissionChecker):
    """통합 권한 확인 클래스"""

    def __init__(self, config: GuardrailConfig):
        self.config = config
        self._auth_client: Optional[UnifiedAuthClient] = None

    async def initialize(self) -> None:
        """권한 확인 클라이언트 초기화"""
        auth_config = AuthConfig(
            strategy=self.config.auth_strategy,  # type: ignore
            enable_cache=self.config.enable_cache,
            cache_ttl=self.config.cache_ttl,
            timeout=self.config.timeout_seconds,
        )

        self._auth_client = UnifiedAuthClient(auth_config)
        logger.info(
            f"Permission checker initialized with strategy: {self.config.auth_strategy.value}"
        )

    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """권한 확인"""
        if not self._auth_client:
            await self.initialize()

        try:
            if not self._auth_client:
                await self.initialize()

            # 타입 체크를 위한 assert 추가
            assert (
                self._auth_client is not None
            ), "Auth client initialization failed"

            result = await self._auth_client.check_permission(
                user_id=user_id,
                resource=resource,
                action=action,
                tenant_id=tenant_id,
                context=context,
            )

            logger.debug(
                f"Permission check: user={user_id}, resource={resource}, "
                f"action={action}, tenant={tenant_id}, allowed={result.allowed}"
            )

            return result.allowed

        except Exception as e:
            logger.error(f"Permission check failed: {e}")

            if self.config.fail_open:
                logger.warning(
                    "Permission check failed, but fail_open=True, allowing access"
                )
                return True

            return False

    async def cleanup(self) -> None:
        """권한 확인 클라이언트 정리"""
        if self._auth_client:
            # UnifiedAuthorizationClient cleanup if needed
            pass
