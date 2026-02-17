from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.api.schemas.request_schema import RequestResponseSchema
from app.api.schemas.user_schema import UserBaseResponseSchema
from app.common.enums import Status


class RequestTrackingResponseSchema(BaseModel):
    id: int
    user: UserBaseResponseSchema
    comment: Optional[str] = None
    status: Status

    model_config = ConfigDict(from_attributes=True)
