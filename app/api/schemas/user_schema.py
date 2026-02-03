# user_schema.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.common.enums import UserRole


class UserRegisterRequest(BaseModel):
    # email: str
    # password: str = Field(min_length=8)
    # first_name: str = Field(min_length=1)
    # last_name: str = Field(min_length=1)

    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserBaseResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    role: UserRole
    created: datetime
    updated: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
