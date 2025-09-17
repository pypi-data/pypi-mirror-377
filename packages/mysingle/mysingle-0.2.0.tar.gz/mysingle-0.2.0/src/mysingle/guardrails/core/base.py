"""가드레일 기본 클래스 및 인터페이스"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .config import GuardrailConfig


class BaseGuardrail(ABC):
    """가드레일 기본 추상 클래스"""

    def __init__(self, config: Optional[GuardrailConfig] = None):
        self.config = config or GuardrailConfig()

    @abstractmethod
    async def initialize(self) -> None:
        """가드레일 초기화"""
        pass

    @abstractmethod
    async def check(self, *args, **kwargs) -> bool:
        """가드레일 검사 수행"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """가드레일 정리 작업"""
        pass


class IPermissionChecker(ABC):
    """권한 확인 인터페이스"""

    @abstractmethod
    async def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """권한 확인"""
        pass


class IRateLimiter(ABC):
    """Rate Limiter 인터페이스"""

    @abstractmethod
    async def check_rate_limit(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        endpoint: str = "default",
    ) -> bool:
        """Rate limit 확인"""
        pass


class IPIIMasker(ABC):
    """PII 마스커 인터페이스"""

    @abstractmethod
    def mask_pii(self, text: str) -> str:
        """PII 마스킹"""
        pass


class IAuditLogger(ABC):
    """감사 로거 인터페이스"""

    @abstractmethod
    async def log_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        allowed: bool,
        tenant_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """접근 로그 기록"""
        pass
