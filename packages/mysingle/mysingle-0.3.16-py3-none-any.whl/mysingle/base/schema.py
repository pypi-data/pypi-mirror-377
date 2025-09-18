"""Base Document as MongoDB Collection"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from beanie import PydanticObjectId
from pydantic import BaseModel, Field


class BaseSchema(
    BaseModel
):  # TODO: 현재 미적용되었으며 향후 적용여부, 적절성 검토 필요
    """Base Pydantic schema for create operations."""

    tenant_id: Optional[str] = None


class BaseRequestSchema(
    BaseSchema
):  # TODO: 현재 미적용되었으며 향후 적용여부, 적절성 검토 필요
    """Base Pydantic schema for request operations."""

    pass


class BaseResponseSchema(BaseSchema):
    """Base Pydantic schema shared across services."""

    id: PydanticObjectId = Field(alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True,
        "arbitrary_types_allowed": True,
        "populate_by_name": True,  # alias와 field name 모두 허용
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: float,
        },
    }
