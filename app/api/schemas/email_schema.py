# app/api/schemas/email_schema.py

from pydantic import BaseModel, EmailStr


class EmailTestRequest(BaseModel):
    to: EmailStr
    subject: str = "Test email"
    body: str = "This is a test email"
    html: str | None = None


class EmailTestResponse(BaseModel):
    status: str
    message: str
