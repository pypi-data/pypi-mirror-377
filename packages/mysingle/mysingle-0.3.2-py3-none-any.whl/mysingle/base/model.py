"""Base Document as MongoDB Collection"""

from datetime import datetime, timezone
from typing import ClassVar, Optional

from beanie import Document
from pydantic import Field


class BaseDoc(Document):
    """Base document for all services"""

    tenant_id: Optional[str] = Field(
        default=None, description="Tenant ID for multitenant isolation"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = None
    idempotency_key: Optional[str] = None

    class Settings:
        """Settings for the base document."""

        name: ClassVar[str] = "base_collection"
        use_state_management = True
        # It is recommended to appropriately override indexes in service-specific models
        indexes = ["tenant_id", ("tenant_id", "created_at")]
