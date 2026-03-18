# app/api/routes/v1/request_router.py

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from starlette import status as http_status

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
from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.security_models import CurrentUser

router = APIRouter(tags=["Requests"])


@router.post(
    "/", response_model=RequestResponseSchema, status_code=http_status.HTTP_201_CREATED
)
def create_request(
    request_in: RequestCreateSchema,
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.create_request(request_in, current_user.id)


@router.get(
    "/",
    summary="Get All requests for admin",
    description="Returns all requests where their current_status is not equal to draft, ordered by update_at date ",
    response_model=list[RequestResponseListSchema],
)
def get_requests(
    status: Optional[List[Status]] = Query(None),
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise BusinessException(
            message="You do not have permission to perform this action",
            status_code=http_status.HTTP_403_FORBIDDEN,
        )
    return service.get_requests_by_statuses(
        [s.value for s in status] if status else None
    )


@router.get(
    "/pending",
    summary="Get requests assigned to the current approver",
    description="Returns all requests that are assigned to the logged-in approver. "
    "The optional `statuses` query parameter can be used to filter requests "
    "by their current status. Only users with the APPROVER role can "
    "access this endpoint.",
    response_model=list[RequestResponseListSchema],
)
def get_approver_requests(
    statuses: Optional[List[Status]] = Query(None, description="Filter by statuses"),
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_requests_for_approver(
        current_user=current_user, statuses=statuses
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


@router.post(
    "/submit",
    response_model=RequestProcessResponseSchema,
    status_code=http_status.HTTP_201_CREATED,
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
    status_code=http_status.HTTP_200_OK,
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
    return service.get_request_details(request_id, current_user)


@router.patch(
    "/{request_id}/process",
    summary="Process request (approve, reject, cancel, in_progress, complete, reject)",
    description="Process a submitted request by changing its status and creating a tracking record. Rejecting requires a mandatory comment. Requests must be in SUBMITTED status for approver and in approved status for admin.",
    response_model=RequestProcessResponseSchema,
)
def process_request(
    background_tasks: BackgroundTasks,
    request_id: int,
    status: Status = Query(...),
    comment: Optional[str] = Query(None),
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.process_request(
        request_id=request_id,
        status_in=status,
        current_user=current_user,
        comment=comment,
        background_tasks=background_tasks,
    )
