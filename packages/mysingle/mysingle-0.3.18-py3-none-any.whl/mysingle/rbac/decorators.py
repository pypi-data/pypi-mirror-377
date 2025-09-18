"""RBAC 데코레이터 모듈 - 권한 확인 및 구독 제한 검사를 위한 데코레이터 제공"""

import functools
from typing import Callable, Optional

from fastapi import HTTPException, Request
from starlette.status import HTTP_403_FORBIDDEN

from mysingle.auth_utils import (
    AuthenticationContext,
    AuthenticationError,
    get_auth_context,
    set_auth_context,
)
from mysingle.logging import get_logger
from mysingle.security.jwt import decode_token

from .exceptions import PermissionDeniedError

logger = get_logger(__name__)


async def _get_subscription_limit(
    tenant_id: str, feature: str, limit_type: str
) -> Optional[int]:
    """테넌트의 구독 제한 정보를 조회합니다.

    Args:
        tenant_id: 테넌트 ID
        feature: 기능명 (예: "journals", "accounts")
        limit_type: 제한 타입 (예: "count", "storage")

    Returns:
        구독 제한값 또는 None (무제한)
    """
    try:
        # TODO: 실제로는 TenantClient를 통해 구독 정보 조회
        # tenant_client = TenantClient()
        # subscription = await tenant_client.get_subscription(tenant_id)
        # return subscription.get_limit(feature, limit_type)

        # 현재는 기본 제한값을 반환 (개발용)
        default_limits = {
            "journals": {"count": 1000},
            "accounts": {"count": 500},
            "users": {"count": 50},
            "storage": {"size": 1024 * 1024 * 1024},  # 1GB
        }

        feature_limits = default_limits.get(feature, {})
        return feature_limits.get(limit_type)

    except Exception as e:
        logger.error(f"Failed to get subscription limit: {e}")
        return None  # 에러 시 제한 없음으로 처리


async def _get_rbac_client():
    """지연 import로 순환 import 방지"""
    from .rbac_client import get_rbac_client

    return await get_rbac_client()


def require_permission(
    resource: str,
    action: str,
    tenant_from_path: bool = True,
    tenant_param: str = "tenant_id",
    user_id_from_token: bool = True,
    user_id_param: str = "user_id",
    context_builder: Optional[Callable] = None,
    rbac_client=None,  # Type hint 제거하여 순환 import 방지
):
    """
    권한 확인 데코레이터

    Args:
        resource: 리소스 명 (예: "ledger:journals")
        action: 액션 (create|read|update|delete)
        tenant_from_path: 경로에서 tenant_id 추출 여부
        tenant_param: tenant_id 매개변수명
        user_id_from_token: JWT 토큰에서 user_id 추출 여부
        user_id_param: user_id 매개변수명
        context_builder: 추가 컨텍스트 빌더 함수
        rbac_client: 사용할 RBAC 클라이언트 (기본: 전역 클라이언트)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # FastAPI Request 객체 찾기
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise HTTPException(
                    status_code=500,
                    detail="Request object not found in function arguments",
                )

            try:
                # 사용자 ID 추출 (통합 인증 유틸리티 사용)
                user_id = None
                if user_id_from_token:
                    # 이미 미들웨어에서 처리된 인증 컨텍스트 확인
                    auth_context = get_auth_context(request)
                    if auth_context:
                        user_id = auth_context.user_id
                    else:
                        # 토큰에서 직접 추출
                        auth_header = request.headers.get("Authorization")
                        if auth_header and auth_header.startswith("Bearer "):
                            token = auth_header[7:]
                            try:
                                payload = decode_token(token)
                                user_id = payload.get("sub")
                            except Exception:
                                raise HTTPException(
                                    status_code=401, detail="Invalid token"
                                )

                if not user_id and user_id_param in kwargs:
                    user_id = kwargs[user_id_param]

                if not user_id:
                    raise HTTPException(
                        status_code=401, detail="User ID not found"
                    )

                # 테넌트 ID 추출
                tenant_id = None
                if tenant_from_path:
                    tenant_id = extract_tenant_from_request(
                        request, tenant_param
                    )

                if not tenant_id and tenant_param in kwargs:
                    tenant_id = kwargs[tenant_param]

                if not tenant_id:
                    raise HTTPException(
                        status_code=400, detail="Tenant ID not found"
                    )

                # 컨텍스트 구성
                context = {"tenant_id": tenant_id}
                if context_builder:
                    additional_context = context_builder(*args, **kwargs)
                    context.update(additional_context)

                # RBAC 클라이언트로 권한 확인
                client = rbac_client or await _get_rbac_client()
                permission_result = await client.check_permission(
                    user_id=user_id,
                    resource=resource,
                    action=action,
                    tenant_id=tenant_id,
                )

                if not permission_result.allowed:
                    logger.warning(
                        f"Permission denied: user={user_id}, resource={resource}, "
                        f"action={action}, tenant_id={tenant_id}"
                    )
                    raise PermissionDeniedError(
                        user_id=user_id,
                        resource=resource,
                        action=action,
                        reason="Insufficient permissions",
                    )

                logger.debug(
                    f"Permission granted: user={user_id}, resource={resource}, "
                    f"action={action}"
                )

                # 인증 컨텍스트 설정
                if not get_auth_context(request):
                    auth_context = AuthenticationContext(
                        user_id=user_id, tenant_id=tenant_id
                    )
                    set_auth_context(request, auth_context)

                return await func(*args, **kwargs)

            except PermissionDeniedError:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="권한이 없습니다"
                )
            except AuthenticationError as e:
                raise HTTPException(status_code=401, detail=str(e))
            except Exception as e:
                logger.error(f"RBAC check failed: {e}")
                raise HTTPException(
                    status_code=500, detail="권한 확인 중 오류가 발생했습니다"
                )

        return wrapper

    return decorator


def require_subscription_limit(
    feature: str,
    limit_type: str = "count",
    current_value_getter: Optional[Callable] = None,
):
    """
    구독 제한 확인 데코레이터

    Args:
        feature: 기능명 (예: "journals", "accounts")
        limit_type: 제한 타입 ("count", "storage" 등)
        current_value_getter: 현재 사용량을 계산하는 함수
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # FastAPI Request 객체 찾기
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise HTTPException(
                    status_code=500,
                    detail="Request object not found in function arguments",
                )

            # 구독 제한 확인 로직
            logger.debug(
                f"Subscription limit check: feature={feature}, limit_type={limit_type}"
            )

            # 실제 구독 제한 확인 로직 구현
            try:
                # 1. Request에서 테넌트 ID 추출
                tenant_id = extract_tenant_from_request(request)
                if not tenant_id:
                    logger.warning(
                        "No tenant_id found for subscription limit check"
                    )
                    # 테넌트 ID가 없으면 제한 없이 진행
                    return await func(*args, **kwargs)

                # 2. 현재 사용량 확인 (제공된 함수 사용)
                current_value = 0
                if current_value_getter:
                    current_value = await current_value_getter(*args, **kwargs)

                # 3. 테넌트 서비스에서 구독 제한 정보 조회 (간소화된 로직)
                # 실제로는 TenantClient를 통해 구독 정보를 조회해야 함
                subscription_limit = await _get_subscription_limit(
                    tenant_id, feature, limit_type
                )

                # 4. 제한 초과 여부 판단
                if (
                    subscription_limit is not None
                    and current_value >= subscription_limit
                ):
                    logger.warning(
                        f"Subscription limit exceeded: tenant={tenant_id}, "
                        f"feature={feature}, current={current_value}, limit={subscription_limit}"
                    )
                    raise HTTPException(
                        status_code=402,  # Payment Required
                        detail=f"Subscription limit exceeded for {feature}. "
                        f"Current: {current_value}, Limit: {subscription_limit}",
                    )

                logger.debug(
                    f"Subscription limit check passed: tenant={tenant_id}, "
                    f"feature={feature}, current={current_value}, limit={subscription_limit}"
                )

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error during subscription limit check: {e}")
                # 에러 발생 시 제한 없이 진행 (가용성 우선)

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def extract_tenant_from_request(
    request: Request, tenant_param: str = "tenant_id"
) -> Optional[str]:
    """Request에서 테넌트 ID 추출"""
    # 경로 매개변수에서 확인
    if tenant_param in request.path_params:
        param_value = request.path_params[tenant_param]
        return str(param_value) if param_value is not None else None

    # 쿼리 매개변수에서 확인
    if tenant_param in request.query_params:
        query_value = request.query_params[tenant_param]
        return str(query_value) if query_value is not None else None

    # HTTP 헤더에서 추출
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        return tenant_id

    return None


def rate_limit(requests_per_minute: int = 60):
    """
    속도 제한 데코레이터

    Args:
        requests_per_minute: 분당 허용 요청 수
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # TODO: 실제 속도 제한 로직 구현
            # Redis를 사용한 sliding window 또는 token bucket 알고리즘
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def audit_log(action: str, resource_type: str):
    """
    감사 로그 데코레이터

    Args:
        action: 수행된 액션
        resource_type: 리소스 타입
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # 실행 전 정보 수집
            start_time = None
            user_id = None
            tenant_id = None

            try:
                import time

                start_time = time.time()

                if request:
                    # 사용자 ID 추출
                    auth_context = get_auth_context(request)
                    if auth_context:
                        user_id = auth_context.user_id
                        tenant_id = auth_context.tenant_id
                    else:
                        # 토큰에서 직접 추출
                        auth_header = request.headers.get("Authorization")
                        if auth_header and auth_header.startswith("Bearer "):
                            token = auth_header[7:]
                            try:
                                payload = decode_token(token)
                                user_id = payload.get("sub")
                            except Exception:  # nosec B110
                                # 토큰 디코딩 실패는 정상적인 케이스
                                pass

                        # 테넌트 ID 추출
                        tenant_id = extract_tenant_from_request(request)

                # 함수 실행
                result = await func(*args, **kwargs)

                # 성공 감사 로그 기록 (AuditLogger 사용)
                execution_time = time.time() - start_time if start_time else 0
                await _log_audit_event(
                    action=action,
                    resource_type=resource_type,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    success=True,
                    execution_time=execution_time,
                    details={
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    },
                )

                return result

            except Exception as e:
                # 실패 감사 로그 기록 (AuditLogger 사용)
                execution_time = time.time() - start_time if start_time else 0
                await _log_audit_event(
                    action=action,
                    resource_type=resource_type,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    success=False,
                    execution_time=execution_time,
                    error=str(e),
                    details={
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys()),
                    },
                )
                raise

        return wrapper

    return decorator


async def _log_audit_event(
    action: str,
    resource_type: str,
    user_id: str | None,
    tenant_id: str | None,
    success: bool,
    execution_time: float,
    error: str | None = None,
    details: dict | None = None,
) -> None:
    """감사 이벤트 로깅을 위한 헬퍼 함수"""
    try:
        # 지연 import로 순환 import 방지
        from ..guardrails.audit.logger import get_audit_logger

        audit_logger = await get_audit_logger()

        # 감사 로그 기록
        await audit_logger.log_security_event(
            event_type="function_execution",
            user_id=user_id,
            tenant_id=tenant_id,
            severity="info" if success else "error",
            details={
                "action": action,
                "resource_type": resource_type,
                "success": success,
                "execution_time_ms": round(execution_time * 1000, 2),
                "error": error,
                **(details or {}),
            },
        )

    except ImportError:
        # AuditLogger를 사용할 수 없는 경우 기본 로깅으로 폴백
        if success:
            logger.info(
                f"AUDIT: {action} {resource_type} - "
                f"user_id={user_id}, tenant_id={tenant_id}, "
                f"status=success, execution_time={execution_time:.3f}s"
            )
        else:
            logger.error(
                f"AUDIT: {action} {resource_type} - "
                f"user_id={user_id}, tenant_id={tenant_id}, "
                f"status=error, error={error}, execution_time={execution_time:.3f}s"
            )
    except Exception as e:
        # 감사 로깅 실패 시 기본 로깅으로 폴백
        logger.warning(f"Failed to log audit event: {e}")
        if success:
            logger.info(
                f"AUDIT: {action} {resource_type} - "
                f"user_id={user_id}, tenant_id={tenant_id}, "
                f"status=success, execution_time={execution_time:.3f}s"
            )
        else:
            logger.error(
                f"AUDIT: {action} {resource_type} - "
                f"user_id={user_id}, tenant_id={tenant_id}, "
                f"status=error, error={error}, execution_time={execution_time:.3f}s"
            )
