# app/api/routes/v1/request_router.py

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from starlette import status

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import (
    get_request_service,
    get_request_tracking_service,
)
from app.api.schemas.request_schema import (
    RequestCreateSchema,
    RequestProcessResponseSchema,
    RequestResponseListSchema,
    RequestResponseSchema,
)
from app.common.enums import Status
from app.common.security_models import CurrentUser

router = APIRouter(tags=["Requests"])


@router.post(
    "/", response_model=RequestResponseSchema, status_code=status.HTTP_201_CREATED
)
def create_request(
    request_in: RequestCreateSchema,
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.create_request(request_in, current_user.id)


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


@router.post(
    "/submit",
    response_model=RequestProcessResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_and_submit_request(
    request_in: RequestCreateSchema,
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.create_and_submit_request(request_in, current_user.id)


@router.patch(
    "/{request_id}/submit",
    response_model=RequestProcessResponseSchema,
    status_code=status.HTTP_200_OK,
)
def submit_request(
    request_id: int,
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.submit_existing_request(
        request_id=request_id,
        current_user_id=current_user.id,
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


@router.post(
    "/{request_id}/process",
    summary="Process request (approve, reject, cancel)",
    description="Process a submitted request by changing its status and creating a tracking record. Rejecting requires a mandatory comment. Requests must be in SUBMITTED status.",
    response_model=RequestResponseSchema,
)
def approve_request(
    background_tasks: BackgroundTasks,
    request_id: int,
    status: Status = Query(...),
    comment: Optional[str] = Query(None),
    service=Depends(get_request_tracking_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.process_request(
        request_id=request_id,
        status_in=status,
        user_id=current_user.id,
        comment=comment,
        background_tasks=background_tasks,
    )
