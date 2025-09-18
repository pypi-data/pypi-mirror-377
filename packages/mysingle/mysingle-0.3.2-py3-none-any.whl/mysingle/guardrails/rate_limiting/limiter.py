"""Rate Limiting 로직"""

import time
from typing import Optional

from mysingle.logging import get_logger

from ..core.base import IRateLimiter
from ..core.config import GuardrailConfig
from .store import InMemoryRateLimitStore

logger = get_logger(__name__)


class RateLimiter(IRateLimiter):
    """Rate Limiter 구현"""

    def __init__(self, config: GuardrailConfig):
        self.config = config
        self._store = InMemoryRateLimitStore()
        self._window_size = 3600  # 1시간 윈도우

    async def check_rate_limit(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        endpoint: str = "default",
    ) -> bool:
        """Rate Limiting 확인"""
        if not self.config.enable_rate_limiting:
            return True

        now = time.time()

        # 키 생성
        key = f"{tenant_id or 'global'}:{user_id}:{endpoint}"

        # 현재 정보 조회
        rate_info = self._store.get_rate_info(key)

        # 윈도우 리셋 확인
        if now - rate_info["window_start"] > self._window_size:
            rate_info = {
                "count": 0,
                "window_start": now,
                "last_request": now,
            }

        # Rate limit 확인
        limit = self.config.tenant_rate_limit.get(
            tenant_id or "default", self.config.default_rate_limit
        )

        if rate_info["count"] >= limit:
            logger.warning(
                f"Rate limit exceeded for {key}: {rate_info['count']}/{limit}"
            )
            return False

        # 요청 카운트 증가
        rate_info["count"] += 1
        rate_info["last_request"] = now

        # 저장소에 업데이트
        self._store.update_rate_info(key, rate_info)

        logger.debug(
            f"Rate limit check passed for {key}: {rate_info['count']}/{limit}"
        )

        return True

    async def get_rate_info(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        endpoint: str = "default",
    ) -> dict:
        """Rate limit 정보 조회"""
        key = f"{tenant_id or 'global'}:{user_id}:{endpoint}"
        rate_info = self._store.get_rate_info(key)

        limit = self.config.tenant_rate_limit.get(
            tenant_id or "default", self.config.default_rate_limit
        )

        return {
            "key": key,
            "current_count": rate_info["count"],
            "limit": limit,
            "remaining": max(0, limit - rate_info["count"]),
            "window_start": rate_info["window_start"],
            "last_request": rate_info["last_request"],
        }

    async def reset_rate_limit(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        endpoint: str = "default",
    ) -> None:
        """Rate limit 리셋"""
        key = f"{tenant_id or 'global'}:{user_id}:{endpoint}"
        self._store.update_rate_info(
            key,
            {
                "count": 0,
                "window_start": time.time(),
                "last_request": time.time(),
            },
        )
        logger.info(f"Rate limit reset for {key}")

    def cleanup_expired(self) -> None:
        """만료된 Rate limit 정보 정리"""
        self._store.cleanup_expired(self._window_size)

    def get_store_stats(self) -> dict:
        """저장소 통계 정보"""
        return {
            "store_size": self._store.get_store_size(),
            "window_size": self._window_size,
            "default_limit": self.config.default_rate_limit,
            "tenant_limits": self.config.tenant_rate_limit,
        }
