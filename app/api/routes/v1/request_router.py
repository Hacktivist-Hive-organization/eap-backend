# app/api/routes/v1/request_router.py

from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from starlette import status as http_status

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import get_request_service
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
    "/",
    summary="Create new draft request",
    description="""
    Creates a new request in draft status after validating the provided request type and subtype. 
    The request is not submitted for processing yet and can be updated or submitted later by the requester.
    """,
    response_model=RequestResponseSchema,
    status_code=http_status.HTTP_201_CREATED,
)
def create_request(
    request_in: RequestCreateSchema,
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.create_request(request_in, current_user=current_user)


@router.get(
    "/",
    summary="Retrieve all non-draft requests (Admin only)",
    description="""
    Returns a list of all requests whose status is not draft, ordered by the last updated date.
    This endpoint is restricted to users with the ADMIN role.
    Optionally filter results using the status query parameter.
    """,
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
    summary="Retrieve requests assigned to the current approver",
    description="""
    Returns all requests assigned to the logged-in approver.
    Optionally filter results by providing one or more statuses.
    Only users with the APPROVER role can access this endpoint.
    """,
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
    summary="Retrieve requests created by the current user",
    description="""
    Returns all requests created by the logged-in requester.
    Optionally filter results using the statuses query parameter.
    This endpoint is intended for users with the REQUESTER role.
    """,
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
    summary="Create and submit new request",
    description="""
    Creates a new request and immediately submits it for processing. 
    The request is automatically assigned to the approver with the lowest workload based on the request type.
    Uses the unified process_request method internally.
    """,
    response_model=RequestProcessResponseSchema,
    status_code=http_status.HTTP_201_CREATED,
)
def create_and_submit_request(
    background_tasks: BackgroundTasks,
    request_in: RequestCreateSchema,
    service=Depends(get_request_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    request = service.create_request(request_in, current_user=current_user)

    return service.process_request(
        request_id=request.id,
        status_in=Status.SUBMITTED,
        current_user=current_user,
        comment="Request submitted on creation",
        background_tasks=background_tasks,
    )


@router.get(
    "/{request_id}",
    summary="Retrieve request details by ID",
    description="""
    Returns the full details of a specific request.
    **Access is restricted to:**
    - The requester who created the request
    - The assigned approver
    - Users with the ADMIN role
    """,
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
    summary="Process a request (status update)",
    description="""
    Updates the status of a request and creates a tracking record for the action.
    Supported actions depend on the user role:
    - Requester: can cancel or reopen a cancelled request
    - Approver: can approve or reject requests
    - Admin: can assign, mark in_progress, complete, or reject approved requests
    A comment is required when rejecting a request.
    """,
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
