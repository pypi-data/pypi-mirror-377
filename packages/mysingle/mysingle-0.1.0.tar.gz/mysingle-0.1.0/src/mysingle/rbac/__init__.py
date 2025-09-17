# py_common.rbac - 공용 권한 관리 데코레이터 (순환 import 방지)

# 공용 데코레이터들 (외부에서 자주 사용)
from .decorators import (
    require_permission,
    require_subscription_limit,
    extract_tenant_from_request,
    rate_limit,
    audit_log,
)

# 공용 예외들
from .exceptions import (
    RBACError,
    PermissionDeniedError,
    RBACServiceUnavailableError,
    RBACCacheError,
    RBACTimeoutError,
)

__all__ = [
    # 데코레이터
    "require_permission",
    "require_subscription_limit",
    "extract_tenant_from_request",
    "rate_limit",
    "audit_log",
    # 예외
    "RBACError",
    "PermissionDeniedError",
    "RBACServiceUnavailableError",
    "RBACCacheError",
    "RBACTimeoutError",
]
