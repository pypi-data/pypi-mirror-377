"""Security utilities for tenant isolation and audit logging."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Type, TypeVar

from beanie.odm.queries.find import FindMany

from mysingle.base.model import BaseDoc

__all__ = ["isolate_tenant", "audit_log"]

logger = logging.getLogger("py_common.audit")

T = TypeVar("T", bound=BaseDoc)


def isolate_tenant(model: Type[T], tenant_id: str) -> FindMany[T]:
    """Return a Beanie query filtered by the given tenant id."""
    return model.find({"tenant_id": tenant_id})


def audit_log(
    actor: str,
    action: str,
    tenant_id: str,
    details: dict[str, Any] | None = None,
) -> None:
    """Emit a structured audit log entry."""
    entry = {
        "actor": actor,
        "action": action,
        "tenant_id": tenant_id,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    logger.info("AUDIT", extra={"audit": entry})
