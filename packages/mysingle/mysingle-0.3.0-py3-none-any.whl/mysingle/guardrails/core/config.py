"""가드레일 설정 및 기본 구성"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict


class AuthStrategy(Enum):
    """권한 확인 전략 (순환 import 방지를 위해 local 정의)"""

    IAM_ONLY = "iam_only"
    RBAC_ONLY = "rbac_only"
    RBAC_FALLBACK = "rbac_fallback"


class PIIDetectionLevel(Enum):
    """PII 감지 레벨"""

    BASIC = "basic"
    ADVANCED = "advanced"
    AI = "ai"


class GuardrailMode(Enum):
    """가드레일 모드"""

    STRICT = "strict"
    PERMISSIVE = "permissive"
    MONITORING = "monitoring"


@dataclass
class GuardrailConfig:
    """통합 가드레일 설정"""

    # 권한 확인 전략
    auth_strategy: AuthStrategy = AuthStrategy.RBAC_FALLBACK
    enable_cache: bool = True
    cache_ttl: int = 300

    # Rate Limiting
    enable_rate_limiting: bool = True
    default_rate_limit: int = 1000  # 1000 requests per hour
    tenant_rate_limit: Dict[str, int] = field(default_factory=dict)

    # PII 보호
    enable_pii_masking: bool = True
    pii_detection_level: str = "advanced"  # basic, advanced, ai

    # 감사 로깅
    enable_audit_logging: bool = True
    audit_sensitive_operations: bool = True

    # 에러 처리
    fail_open: bool = False  # True면 권한 확인 실패 시 접근 허용
    timeout_seconds: float = 5.0
