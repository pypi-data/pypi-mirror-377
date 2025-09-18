"""RBAC 관련 예외 클래스"""


class RBACError(Exception):
    """RBAC 기본 예외"""

    def __init__(self, message: str, code: str = "RBAC_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class PermissionDeniedError(RBACError):
    """권한 거부 예외"""

    def __init__(
        self,
        user_id: str,
        resource: str,
        action: str,
        reason: str = "Permission denied",
    ):
        self.user_id = user_id
        self.resource = resource
        self.action = action
        message = f"Permission denied for user {user_id} on {resource}:{action} - {reason}"
        super().__init__(message, "PERMISSION_DENIED")


class RBACServiceUnavailableError(RBACError):
    """RBAC 서비스 사용 불가 예외"""

    def __init__(self, service_url: str, reason: str = "Service unavailable"):
        self.service_url = service_url
        message = f"RBAC service unavailable at {service_url}: {reason}"
        super().__init__(message, "RBAC_SERVICE_UNAVAILABLE")


class RBACCacheError(RBACError):
    """캐시 관련 예외"""

    def __init__(self, cache_key: str, reason: str = "Cache error"):
        self.cache_key = cache_key
        message = f"Cache error for key {cache_key}: {reason}"
        super().__init__(message, "RBAC_CACHE_ERROR")


class RBACTimeoutError(RBACError):
    """RBAC 서비스 타임아웃 예외"""

    def __init__(self, timeout_seconds: float, operation: str = "unknown"):
        self.timeout_seconds = timeout_seconds
        self.operation = operation
        message = (
            f"RBAC operation '{operation}' timed out after {timeout_seconds}s"
        )
        super().__init__(message, "RBAC_TIMEOUT")
