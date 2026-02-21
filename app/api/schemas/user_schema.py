# app/api/schemas/user_schema.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import UserRole


class UserRegisterRequestSchema(BaseModel):
    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserLoginRequestSchema(BaseModel):
    email: str
    password: str


class UserSelfUpdateRequestSchema(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)


class UserSelfPartialUpdateRequestSchema(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    is_out_of_office: bool | None = None


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


class ForgotPasswordRequestSchema(BaseModel):
    email: str


class ResetPasswordRequestSchema(BaseModel):
    token: str
    new_password: str
