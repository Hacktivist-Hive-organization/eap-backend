# app/api/routes/v1/email_router.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr

from app.api.dependencies.service_dependency import get_email_manager
from app.infrastructure.email.manager import EmailManager

router = APIRouter(prefix="", tags=["email"])


class EmailTestRequest(BaseModel):
    to: EmailStr
    subject: str = "Test email"
    body: str = "This is a test email"
    html: str | None = None


@router.post("/send")
async def send_test_email(
    request: EmailTestRequest, manager: EmailManager = Depends(get_email_manager)
):
    await manager.send_email(
        to=str(request.to),
        subject=request.subject,
        body=request.body,
        html=request.html,
    )
    return {"status": "ok", "message": f"Email sent to {request.to}"}
