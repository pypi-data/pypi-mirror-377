"""Rate Limit 저장소"""

import time
from typing import Any, Dict


class InMemoryRateLimitStore:
    """메모리 기반 Rate Limit 저장소"""

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}

    def get_rate_info(self, key: str) -> Dict[str, Any]:
        """Rate limit 정보 조회"""
        return self._store.get(
            key,
            {
                "count": 0,
                "window_start": time.time(),
                "last_request": time.time(),
            },
        )

    def update_rate_info(self, key: str, info: Dict[str, Any]) -> None:
        """Rate limit 정보 업데이트"""
        self._store[key] = info

    def cleanup_expired(self, window_size: int = 3600) -> None:
        """만료된 항목 정리"""
        now = time.time()
        expired_keys = [
            key
            for key, info in self._store.items()
            if now - info.get("window_start", 0) > window_size * 2
        ]

        for key in expired_keys:
            del self._store[key]

    def get_store_size(self) -> int:
        """저장소 크기 반환"""
        return len(self._store)


class RedisRateLimitStore:
    """Redis 기반 Rate Limit 저장소 (향후 구현)"""

    def __init__(self, redis_client=None):
        self.redis_client = redis_client

    async def get_rate_info(self, key: str) -> Dict[str, Any]:
        """Rate limit 정보 조회"""
        # TODO: Redis 구현
        raise NotImplementedError("Redis rate limit store not implemented yet")

    async def update_rate_info(self, key: str, info: Dict[str, Any]) -> None:
        """Rate limit 정보 업데이트"""
        # TODO: Redis 구현
        raise NotImplementedError("Redis rate limit store not implemented yet")
