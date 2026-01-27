# user_schema.py

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    # email: str
    # password: str = Field(min_length=8)
    # first_name: str = Field(min_length=1)
    # last_name: str = Field(min_length=1)

    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
