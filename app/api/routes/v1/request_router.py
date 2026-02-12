# app/api/routes/v1/request_router.py

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import get_request_service
from app.api.schemas.request_schema import (
    RequestCreateSchema,
    RequestResponseListSchema,
    RequestResponseSchema,
)
from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.models.security_models import CurrentUser

router = APIRouter(tags=["Requests"])


@router.post("/", response_model=RequestResponseSchema)
def create_request(
    request_in: RequestCreateSchema,
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.role == UserRole.REQUESTER:
        return service.create_request(request_in, current_user.id)
    raise BusinessException(
        message="You do not have permission to create request",
        status_code=status.HTTP_403_FORBIDDEN,
    )


@router.get(
    "/my-requests",
    summary="Get all requests by user",
    description="Get all user requests by status order by creation date",
    response_model=List[RequestResponseListSchema],
)
def get_requests_by_user(
    statuses: Optional[List[Status]] = Query(None),
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_requests_by_user(
        current_user.id, [s.value for s in statuses] if statuses else None
    )


@router.get(
    "/{request_id}",
    summary="Get request details",
    description="Get full request details by id (requester only)",
    response_model=RequestResponseSchema,
)
def get_request_details(
    request_id: int,
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_request_details(request_id, current_user.id)
