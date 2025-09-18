"""FastAPI 권한 확인 의존성"""

from typing import Any, Dict, Optional

from fastapi import Depends, Header, HTTPException, Request

from mysingle.auth_utils import get_auth_context

from ..core.config import GuardrailConfig
from .permission_checker import PermissionChecker

# 전역 권한 확인자
_permission_checker: Optional[PermissionChecker] = None


async def get_permission_checker(
    config: Optional[GuardrailConfig] = None,
) -> PermissionChecker:
    """권한 확인자 싱글톤 인스턴스 반환"""
    global _permission_checker
    if _permission_checker is None:
        _permission_checker = PermissionChecker(config or GuardrailConfig())
        await _permission_checker.initialize()
    return _permission_checker


async def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
    """테넌트 ID 추출 (기존 가드레일과 호환)"""
    if x_tenant_id is None:
        raise HTTPException(
            status_code=400, detail="X-Tenant-Id header missing"
        )
    return x_tenant_id


async def check_permission(
    resource: str,
    action: str,
    request: Request,
    tenant_id: Optional[str] = Depends(get_tenant_id),
    context: Optional[Dict[str, Any]] = None,
) -> None:
    """권한 확인 의존성"""
    try:
        auth_context = get_auth_context(request)
        if not auth_context:
            raise HTTPException(
                status_code=401, detail="Authentication context not found"
            )

        checker = await get_permission_checker()

        # 권한 확인
        allowed = await checker.check_permission(
            user_id=auth_context.user_id,
            resource=resource,
            action=action,
            tenant_id=tenant_id,
            context=context,
        )

        if not allowed:
            raise HTTPException(status_code=403, detail="Permission denied")

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500, detail="Authorization system error"
        )


def require_permission(resource: str, action: str):
    """권한 확인 데코레이터 팩토리"""

    async def _check_permission(
        request: Request,
        tenant_id: str = Depends(get_tenant_id),
    ) -> None:
        await check_permission(resource, action, request, tenant_id)

    return Depends(_check_permission)
