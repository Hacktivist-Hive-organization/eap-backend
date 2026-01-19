from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    username: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    username: EmailStr
    is_active: bool

    class Config:
        orm_mode = True

class UserLoginRequest(BaseModel):
    username: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
