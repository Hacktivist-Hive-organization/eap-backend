from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
