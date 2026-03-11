# app/api/schemas/request_tracking_schema.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.api.schemas.user_schema import UserBaseResponseSchema
from app.common.enums import Status


class RequestTrackingResponseSchema(BaseModel):
    id: int
    user: UserBaseResponseSchema
    comment: Optional[str] = None
    status: Status
    created_at: datetime

    class ConfigDict:
        from_attributes = True
