# app/api/schemas/user_schema.py

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator

from app.common.enums import UserRole


class UserRegisterRequestSchema(BaseModel):
    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserLoginRequestSchema(BaseModel):
    email: str
    password: str


class ForgotPasswordRequestSchema(BaseModel):
    email: str


class ResetPasswordRequestSchema(BaseModel):
    token: str
    new_password: str


class ResendVerificationEmailRequestSchema(BaseModel):
    email: str


class UserSelfUpdateRequestSchema(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=255)
    last_name: str | None = Field(default=None, min_length=1, max_length=255)
    is_out_of_office: Annotated[StrictBool, Field(default=None)] = None

    model_config = dict(extra="ignore")

    @field_validator("first_name", "last_name")
    @classmethod
    def first_name_not_blank(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("field cannot be blank or whitespace")
        return v


class UserAdminUpdateRequestSchema(UserSelfUpdateRequestSchema):
    role: UserRole | None = None
    is_active: bool | None = None


class UserBaseResponseSchema(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: UserRole
    is_out_of_office: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminUserResponseSchema(UserBaseResponseSchema):
    created: datetime
    updated: datetime
    is_active: bool


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBaseResponseSchema
