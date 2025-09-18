"""가드레일 시스템 - 모듈형 아키텍처"""

from __future__ import annotations

from .auth.dependencies import (
    check_permission,
    get_auth_context,
    get_permission_checker,
    get_tenant_id,
    require_permission,
)
from .core.base import BaseGuardrail

# Core 구성 요소만 자동 노출 (순환 참조 없음)
from .core.config import GuardrailConfig, GuardrailMode, PIIDetectionLevel
from .privacy.pii_masker import mask_pii_quick

__all__ = [
    # Core (순환 참조 없음)
    "GuardrailConfig",
    "PIIDetectionLevel",
    "GuardrailMode",
    "BaseGuardrail",
    # 하위 호환성 함수들
    # 레거시 함수
    "mask_pii_quick",
    "get_tenant_id",
    "check_permission",
    "require_permission",
    "get_auth_context",
    "get_permission_checker",
]

# # Regular expression patterns for common PII
# EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
# PHONE_RE = re.compile(
#     r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b"
# )
# CARD_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


# def mask_pii(text: str) -> str:
#     """Mask common PII patterns within *text*. (레거시 함수)"""
#     masked = EMAIL_RE.sub("[EMAIL]", text)
#     masked = PHONE_RE.sub("[PHONE]", masked)
#     masked = CARD_RE.sub("[CARD]", masked)
#     return masked


# async def get_tenant_id(x_tenant_id: str | None = Header(default=None)) -> str:
#     """Extract tenant id from headers or raise error. (레거시 함수)"""
#     if x_tenant_id is None:
#         raise HTTPException(status_code=400, detail="X-Tenant-Id header missing")
#     return x_tenant_id


# async def authorize(
#     tenant_id: str = Depends(get_tenant_id),
#     group_id: Optional[str] = None,
#     role: Optional[str] = None,
#     x_user_claims: str | None = Header(default=None, alias="X-User-Claims"),
# ) -> None:
#     """Validate user claims for the given tenant, group, and role. (레거시 함수)

#     ⚠️  이 함수는 레거시 지원을 위해 유지됩니다.
#     새로운 프로젝트에서는 unified_authorize를 사용하세요.
#     """
#     if x_user_claims is None:
#         raise HTTPException(status_code=401, detail="X-User-Claims header missing")
#     try:
#         claims = json.loads(x_user_claims)
#     except Exception as exc:  # pragma: no cover - invalid JSON
#         raise HTTPException(status_code=400, detail="Invalid user claims") from exc
#     if claims.get("tenant_id") != tenant_id:
#         raise HTTPException(status_code=403, detail="Tenant mismatch")
#     if group_id and group_id not in claims.get("groups", []):
#         raise HTTPException(status_code=403, detail="Insufficient group")
#     if role and role not in claims.get("roles", []):
#         raise HTTPException(status_code=403, detail="Insufficient role")


# def check_cost(current_cost: float, new_cost: float, budget: float | None) -> None:
#     """Ensure that adding *new_cost* does not exceed *budget*. (레거시 함수)"""
#     if budget is not None and current_cost + new_cost > budget:
#         raise HTTPException(status_code=403, detail="cost budget exceeded")
