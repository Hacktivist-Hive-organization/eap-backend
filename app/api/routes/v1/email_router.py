# app/api/routes/v1/email_router.py

from fastapi import APIRouter, Depends

from app.api.dependencies.service_dependency import get_email_manager
from app.api.schemas.email_schema import (
    EmailTestRequest,
    EmailTestResponse,
)
from app.infrastructure.email.manager import EmailManager

router = APIRouter(prefix="", tags=["email"])


@router.post("/send", response_model=EmailTestResponse)
async def send_test_email(
    request: EmailTestRequest,
    manager: EmailManager = Depends(get_email_manager),
):
    await manager.send_email(
        to=str(request.to),
        subject=request.subject,
        body=request.body,
        html=request.html,
    )

    return EmailTestResponse(
        status="ok",
        message=f"Email sent to {request.to}",
    )
