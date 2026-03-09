# app/api/schemas/request_schema.py

import re
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, field_validator

from app.api.schemas.request_tracking_schema import RequestTrackingResponseSchema
from app.api.schemas.user_schema import AdminUserResponseSchema, UserBaseResponseSchema
from app.common.enums import Priority, Status


# --- request input ---
class RequestCreateSchema(BaseModel):
    type_id: int
    subtype_id: int
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=20, max_length=2000)
    business_justification: str = Field(min_length=20, max_length=1000)
    priority: Priority

    @field_validator("title", "description", "business_justification")
    def must_contain_letters(cls, v, info):
        if not re.search(r"[A-Za-z]", v):
            raise ValueError(f"{info.field_name} must contain at least one letter")
        return v


# --- response schemas ---
class RequestTypeSchema(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True


class RequestSubtypeSchema(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True


class RequestResponseSchema(BaseModel):
    id: int
    title: str
    priority: Priority
    current_status: Status
    description: str
    business_justification: str
    type: RequestTypeSchema
    subtype: RequestSubtypeSchema
    requester: UserBaseResponseSchema
    assignee: UserBaseResponseSchema | None = None
    created_at: datetime
    updated_at: datetime | None

    class ConfigDict:
        from_attributes = True


class RequestResponseListSchema(BaseModel):
    id: int
    title: str
    priority: Priority
    current_status: Status
    type: RequestTypeSchema
    subtype: RequestSubtypeSchema
    requester: AdminUserResponseSchema
    assignee: UserBaseResponseSchema | None = None
    created_at: datetime
    updated_at: datetime | None

    class ConfigDict:
        from_attributes = True


class RequestSubmitResponseSchema(BaseModel):
    id: int
    title: str
    priority: Priority
    current_status: Status
    type: RequestTypeSchema
    subtype: RequestSubtypeSchema
    requester: AdminUserResponseSchema
    created_at: datetime
    updated_at: datetime | None
    req_tracking: list[RequestTrackingResponseSchema]

    class ConfigDict:
        from_attributes = True
