# app/api/schemas/request_schema.py
import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.common.enums import Priority, Status


class RequestCreateSchema(BaseModel):
    type_id: int
    subtype_id: int
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=20, max_length=2000)
    business_justification: str = Field(min_length=20, max_length=1000)
    priority: Priority
    requester_id: int

    @field_validator("title", "description", "business_justification")
    def must_contain_letters(cls, v, info):
        if not re.search(r"[A-Za-z]", v):
            raise ValueError(f"{info.field_name} must contain at least one letter")
        return v


# ------responses schema ---
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
    description: str
    business_justification: str
    priority: Priority
    status: Status
    type: RequestTypeSchema
    subtype: RequestSubtypeSchema
    created_at: datetime
    updated_at: datetime | None

    class ConfigDict:
        from_attributes = True
