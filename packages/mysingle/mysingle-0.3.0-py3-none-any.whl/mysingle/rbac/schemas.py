from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class PermissionRequest(BaseModel):
    """권한 확인 요청"""

    user_id: str
    resource: str
    action: str
    tenant_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class PermissionResult(BaseModel):
    """권한 확인 결과"""

    allowed: bool
    reason: Optional[str] = None
    matched_policies: List[str] = []
    cached: bool = False
    response_time_ms: float = 0.0


class BatchPermissionRequest(BaseModel):
    """배치 권한 확인 요청"""

    user_id: str
    tenant_id: Optional[str] = None
    permissions: List[Dict[str, str]]
