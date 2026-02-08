# app/api/schemas/user_schema.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import UserRole


class UserRegisterRequest(BaseModel):
    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserSelfUpdateRequest(BaseModel):
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)


class UserSelfPartialUpdateRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserBaseResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBaseResponse):
    created: datetime
    updated: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBaseResponse
