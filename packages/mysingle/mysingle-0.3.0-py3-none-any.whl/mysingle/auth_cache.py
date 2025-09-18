"""통합 권한 캐시 전략 - 권한 확인 결과 캐싱"""

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, Optional

from mysingle.config import settings
from mysingle.rbac.cache import LocalCache, RedisCache
from mysingle.rbac.schemas import PermissionResult

from .logging import get_logger

logger = get_logger(__name__)


class CacheLevel(Enum):
    """캐시 레벨"""

    LOCAL_ONLY = "local"  # 로컬 메모리만
    REDIS_ONLY = "redis"  # Redis만
    DUAL_LAYER = "dual"  # 로컬 + Redis 다층


@dataclass
class AuthCacheConfig:
    """권한 캐시 설정"""

    cache_level: CacheLevel = CacheLevel.DUAL_LAYER
    local_ttl: int = 60  # 로컬 캐시 TTL (1분)
    redis_ttl: int = 300  # Redis 캐시 TTL (5분)
    max_local_size: int = 1000  # 로컬 캐시 최대 크기
    enable_negative_cache: bool = True  # 거부 결과 캐싱 여부
    negative_cache_ttl: int = 30  # 거부 결과 캐시 TTL


class UnifiedAuthCache:
    """통합 권한 캐시

    권한 확인 결과를 효율적으로 캐싱하여 성능을 향상시킵니다.
    로컬 메모리와 Redis를 조합한 다층 캐싱을 지원합니다.
    """

    def __init__(self, config: Optional[AuthCacheConfig] = None):
        self.config = config or AuthCacheConfig()

        # 로컬 캐시 초기화
        self.local_cache = LocalCache(
            max_size=self.config.max_local_size,
            default_ttl=self.config.local_ttl,
        )

        # Redis 캐시 초기화
        self.redis_cache = None
        if self.config.cache_level in [
            CacheLevel.REDIS_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            redis_url = getattr(
                settings, "redis_url", "redis://localhost:6379"
            )
            self.redis_cache = RedisCache(
                redis_url=redis_url,
                default_ttl=self.config.redis_ttl,
            )

    async def connect(self) -> bool:
        """캐시 연결 초기화"""
        if self.redis_cache:
            return await self.redis_cache.connect()
        return True

    def _build_cache_key(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        strategy: str = "default",
    ) -> str:
        """캐시 키 생성"""
        # 기본 키 요소
        key_parts = [
            f"auth:{strategy}",
            f"user:{user_id}",
            f"resource:{resource}",
            f"action:{action}",
        ]

        # 테넌트 ID 추가
        if tenant_id:
            key_parts.append(f"tenant:{tenant_id}")

        # 컨텍스트 해시 추가 (있는 경우)
        if context:
            context_str = json.dumps(context, sort_keys=True)
            context_hash = hashlib.md5(context_str.encode()).hexdigest()[:8]
            key_parts.append(f"ctx:{context_hash}")

        return ":".join(key_parts)

    async def get_permission_result(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        strategy: str = "default",
    ) -> Optional[PermissionResult]:
        """권한 확인 결과 조회"""
        cache_key = self._build_cache_key(
            user_id, resource, action, tenant_id, context, strategy
        )

        # 1. 로컬 캐시에서 조회
        if self.config.cache_level in [
            CacheLevel.LOCAL_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            local_result = self.local_cache.get(cache_key)
            if local_result is not None:
                try:
                    result = PermissionResult(**local_result)
                    result.cached = True
                    logger.debug(f"Cache hit (local): {cache_key}")
                    return result
                except (TypeError, ValueError) as e:
                    logger.warning(f"Invalid cached data in local cache: {e}")
                    self.local_cache.delete(cache_key)

        # 2. Redis 캐시에서 조회
        if self.redis_cache and self.config.cache_level in [
            CacheLevel.REDIS_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            redis_result = await self.redis_cache.get(cache_key)
            if redis_result is not None:
                try:
                    result = PermissionResult(**redis_result)
                    result.cached = True

                    # 로컬 캐시에도 저장 (다층 캐싱)
                    if self.config.cache_level == CacheLevel.DUAL_LAYER:
                        self.local_cache.set(cache_key, asdict(result))

                    logger.debug(f"Cache hit (redis): {cache_key}")
                    return result
                except (TypeError, ValueError) as e:
                    logger.warning(f"Invalid cached data in Redis: {e}")
                    await self.redis_cache.delete(cache_key)

        return None

    async def set_permission_result(
        self,
        user_id: str,
        resource: str,
        action: str,
        result: PermissionResult,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        strategy: str = "default",
    ) -> bool:
        """권한 확인 결과 저장"""
        # 거부 결과 캐싱 설정 확인
        if not result.allowed and not self.config.enable_negative_cache:
            return True

        cache_key = self._build_cache_key(
            user_id, resource, action, tenant_id, context, strategy
        )

        # TTL 결정 (거부 결과는 더 짧은 TTL)
        if not result.allowed and self.config.enable_negative_cache:
            local_ttl = min(
                self.config.negative_cache_ttl, self.config.local_ttl
            )
            redis_ttl = min(
                self.config.negative_cache_ttl, self.config.redis_ttl
            )
        else:
            local_ttl = self.config.local_ttl
            redis_ttl = self.config.redis_ttl

        result_dict = asdict(result)
        result_dict["cached"] = True

        success = True

        # 1. 로컬 캐시에 저장
        if self.config.cache_level in [
            CacheLevel.LOCAL_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            try:
                self.local_cache.set(cache_key, result_dict, ttl=local_ttl)
                logger.debug(f"Cached to local: {cache_key}")
            except Exception as e:
                logger.error(f"Failed to cache to local: {e}")
                success = False

        # 2. Redis 캐시에 저장
        if self.redis_cache and self.config.cache_level in [
            CacheLevel.REDIS_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            try:
                await self.redis_cache.set(
                    cache_key, result_dict, ttl=redis_ttl
                )
                logger.debug(f"Cached to redis: {cache_key}")
            except Exception as e:
                logger.error(f"Failed to cache to Redis: {e}")
                success = False

        return success

    async def invalidate_user_cache(self, user_id: str) -> bool:
        """사용자별 캐시 무효화"""
        pattern = f"auth:*:user:{user_id}:*"

        # 로컬 캐시 무효화
        if self.config.cache_level in [
            CacheLevel.LOCAL_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            keys_to_delete = [
                key
                for key in self.local_cache._cache.keys()
                if f"user:{user_id}" in key
            ]
            for key in keys_to_delete:
                self.local_cache.delete(key)

        # Redis 캐시 무효화
        if self.redis_cache and self.config.cache_level in [
            CacheLevel.REDIS_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            try:
                # Redis 패턴 삭제 기능 사용
                deleted_count = await self.redis_cache.delete_pattern(pattern)
                logger.info(
                    f"Deleted {deleted_count} Redis keys for user {user_id}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to invalidate Redis cache for user {user_id}: {e}"
                )
                return False

        logger.info(f"Invalidated cache for user: {user_id}")
        return True

    async def clear_all_cache(self) -> bool:
        """모든 캐시 삭제"""
        success = True

        # 로컬 캐시 삭제
        if self.config.cache_level in [
            CacheLevel.LOCAL_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            try:
                self.local_cache.clear()
            except Exception as e:
                logger.error(f"Failed to clear local cache: {e}")
                success = False

        # Redis 캐시 삭제
        if self.redis_cache and self.config.cache_level in [
            CacheLevel.REDIS_ONLY,
            CacheLevel.DUAL_LAYER,
        ]:
            try:
                # 모든 auth:* 패턴 키 삭제
                deleted_count = await self.redis_cache.delete_pattern("auth:*")
                logger.info(f"Deleted {deleted_count} Redis auth cache keys")
            except Exception as e:
                logger.error(f"Failed to clear Redis cache: {e}")
                success = False

        logger.info("Cleared all auth cache")
        return success

    async def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 조회"""
        stats = {
            "config": asdict(self.config),
            "local_cache_size": len(self.local_cache._cache),
            "timestamp": time.time(),
        }

        if self.redis_cache:
            try:
                # Redis 연결 상태 확인
                if self.redis_cache._connected:
                    stats["redis_connected"] = True
                    # Redis 메모리 사용량 등 추가 정보는 필요시 구현
                else:
                    stats["redis_connected"] = False
            except Exception:
                stats["redis_connected"] = False

        return stats


# 전역 캐시 인스턴스 (싱글톤)
_unified_cache: Optional[UnifiedAuthCache] = None


async def get_unified_auth_cache(
    config: Optional[AuthCacheConfig] = None,
) -> UnifiedAuthCache:
    """통합 권한 캐시 싱글톤 인스턴스 반환"""
    global _unified_cache
    if _unified_cache is None:
        _unified_cache = UnifiedAuthCache(config)
        await _unified_cache.connect()
    return _unified_cache
