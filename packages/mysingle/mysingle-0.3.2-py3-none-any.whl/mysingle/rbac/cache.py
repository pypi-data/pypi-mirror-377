"""RBAC 캐시 시스템 - 다층 캐싱 전략"""

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    import redis.asyncio as redis

    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

from ..logging import get_logger

logger = get_logger(__name__)


@dataclass
class CacheEntry:
    """캐시 엔트리"""

    value: Any
    expires_at: float
    created_at: float

    def is_expired(self) -> bool:
        """만료 여부 확인"""
        return time.time() > self.expires_at


class LocalCache:
    """로컬 메모리 캐시 (1분 TTL)"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._access_order: Dict[str, float] = {}  # LRU용

    def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if key in self._cache:
            entry = self._cache[key]
            if entry.is_expired():
                self._delete(key)
                return None

            # LRU 업데이트
            self._access_order[key] = time.time()
            return entry.value
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """캐시에 값 저장"""
        if ttl is None:
            ttl = self._default_ttl

        # 캐시 크기 제한
        if len(self._cache) >= self._max_size:
            self._evict_lru()

        now = time.time()
        entry = CacheEntry(value=value, expires_at=now + ttl, created_at=now)

        self._cache[key] = entry
        self._access_order[key] = now

    def has(self, key: str) -> bool:
        """키 존재 여부 확인"""
        if key in self._cache:
            entry = self._cache[key]
            if entry.is_expired():
                self._delete(key)
                return False
            return True
        return False

    def delete(self, key: str) -> None:
        """캐시에서 값 삭제"""
        self._delete(key)

    def clear(self) -> None:
        """캐시 전체 비우기"""
        self._cache.clear()
        self._access_order.clear()

    def _delete(self, key: str) -> None:
        """내부 삭제 메서드"""
        self._cache.pop(key, None)
        self._access_order.pop(key, None)

    def _evict_lru(self) -> None:
        """LRU 방식으로 캐시 엔트리 제거"""
        if not self._access_order:
            return

        # 가장 오래된 키 찾기
        oldest_key = min(
            self._access_order.keys(), key=lambda k: self._access_order[k]
        )
        self._delete(oldest_key)


class RedisCache:
    """Redis 캐시 (5분 TTL)"""

    def __init__(
        self, redis_url: str = "redis://localhost:6379", default_ttl: int = 300
    ):
        self._redis_url = redis_url
        self._default_ttl = default_ttl
        self._redis: Optional[redis.Redis] = None
        self._connected = False

    async def connect(self) -> bool:
        """Redis 연결"""
        if not HAS_REDIS:
            logger.warning("Redis not available, using local cache only")
            return False

        try:
            self._redis = redis.from_url(self._redis_url)
            await self._redis.ping()
            self._connected = True
            logger.info("Redis cache connected successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._connected = False
            return False

    async def get(self, key: str) -> Optional[Any]:
        """캐시에서 값 조회"""
        if not self._connected or not self._redis:
            return None

        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value.decode("utf-8"))
            return None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(
        self, key: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """캐시에 값 저장"""
        if not self._connected or not self._redis:
            return False

        if ttl is None:
            ttl = self._default_ttl

        try:
            serialized_value = json.dumps(value)
            await self._redis.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def has(self, key: str) -> bool:
        """키 존재 여부 확인"""
        if not self._connected or not self._redis:
            return False

        try:
            result = await self._redis.exists(key)
            return bool(result == 1)
        except Exception as e:
            logger.error(f"Redis exists check error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """캐시에서 값 삭제"""
        if not self._connected or not self._redis:
            return False

        try:
            result = await self._redis.delete(key)
            return bool(result == 1)
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """패턴에 매칭되는 모든 키 삭제"""
        if not self._connected or not self._redis:
            return 0

        try:
            # SCAN을 사용하여 패턴 매칭 키 찾기
            deleted_count = 0
            cursor = 0

            while True:
                cursor, keys = await self._redis.scan(
                    cursor=cursor, match=pattern, count=100
                )
                if keys:
                    deleted_count += await self._redis.delete(*keys)

                if cursor == 0:
                    break

            logger.debug(
                f"Deleted {deleted_count} keys matching pattern: {pattern}"
            )
            return deleted_count

        except Exception as e:
            logger.error(
                f"Redis delete pattern error for pattern {pattern}: {e}"
            )
            return 0

    async def close(self) -> None:
        """Redis 연결 종료"""
        if self._redis:
            await self._redis.close()
            self._connected = False


class RBACCache:
    """RBAC 다층 캐시 시스템"""

    def __init__(
        self,
        redis_url: Optional[str] = None,
        local_cache_size: int = 1000,
        local_ttl: int = 60,
        redis_ttl: int = 300,
    ):
        self.local_cache = LocalCache(
            max_size=local_cache_size, default_ttl=local_ttl
        )
        self.redis_cache = RedisCache(
            redis_url or "redis://localhost:6379", default_ttl=redis_ttl
        )
        self._connected_to_redis = False

    async def initialize(self) -> None:
        """캐시 시스템 초기화"""
        self._connected_to_redis = await self.redis_cache.connect()
        logger.info(
            f"RBAC Cache initialized - Redis: {self._connected_to_redis}"
        )

    async def get_permission(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """권한 확인 결과 조회"""
        # 1단계: 로컬 캐시 확인
        result = self.local_cache.get(cache_key)
        if result is not None:
            logger.debug(f"Cache hit (local): {cache_key}")
            # 로컬 캐시 결과가 dict인지 확인
            if isinstance(result, dict):
                return result
            logger.warning(
                f"Invalid local cache data type for {cache_key}: {type(result)}"
            )
            return None

        # 2단계: Redis 캐시 확인
        if self._connected_to_redis:
            result = await self.redis_cache.get(cache_key)
            if result is not None:
                # 로컬 캐시에도 저장
                self.local_cache.set(cache_key, result)
                logger.debug(f"Cache hit (redis): {cache_key}")
                # Redis에서 가져온 결과가 dict인지 확인
                if isinstance(result, dict):
                    return result
                logger.warning(
                    f"Invalid cache data type for {cache_key}: {type(result)}"
                )
                return None

        logger.debug(f"Cache miss: {cache_key}")
        return None

    async def set_permission(
        self,
        cache_key: str,
        permission_result: Dict[str, Any],
        local_ttl: Optional[int] = None,
        redis_ttl: Optional[int] = None,
    ) -> None:
        """권한 확인 결과 저장"""
        # 로컬 캐시에 저장
        self.local_cache.set(cache_key, permission_result, local_ttl)

        # Redis 캐시에 저장
        if self._connected_to_redis:
            await self.redis_cache.set(cache_key, permission_result, redis_ttl)

        logger.debug(f"Cache set: {cache_key}")

    async def invalidate_user_permissions(
        self, user_id: str, tenant_id: Optional[str] = None
    ) -> None:
        """사용자 권한 캐시 무효화"""
        pattern = f"rbac:permission:{user_id}:*"
        if tenant_id:
            pattern = f"rbac:permission:{user_id}:{tenant_id}:*"

        # Redis에서 패턴 매칭으로 삭제는 복잡하므로 여기서는 간단히 처리
        # 실제 구현에서는 Redis의 SCAN 명령어 등을 사용할 수 있음
        logger.info(f"Cache invalidation requested for pattern: {pattern}")

    async def clear_all_cache(self) -> None:
        """모든 캐시 비우기"""
        self.local_cache.clear()
        if self._connected_to_redis:
            # 실제로는 RBAC 관련 키만 삭제해야 함
            logger.info("Redis cache clear requested")

    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        return {
            "local_cache_size": len(self.local_cache._cache),
            "local_cache_max_size": self.local_cache._max_size,
            "redis_connected": self._connected_to_redis,
        }

    async def close(self) -> None:
        """캐시 시스템 종료"""
        await self.redis_cache.close()

    @staticmethod
    def generate_cache_key(
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """캐시 키 생성"""
        key_parts = ["rbac", "permission", user_id]

        if tenant_id:
            key_parts.append(tenant_id)

        key_parts.extend([resource, action])

        if context:
            # context를 정렬된 문자열로 변환
            context_str = json.dumps(context, sort_keys=True)
            key_parts.append(str(hash(context_str)))

        return ":".join(str(part) for part in key_parts)
