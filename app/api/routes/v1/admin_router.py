# app/api/routes/v1/admin_router.py
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Query
from fastapi import status as http_status

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import (
    get_request_service,
)
from app.api.schemas.request_schema import (
    RequestProcessResponseSchema,
    RequestResponseListSchema,
)
from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.security_models import CurrentUser

router = APIRouter(tags=["Admin"])


@router.get(
    "/requests",
    summary="Get All requests",
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


@router.patch(
    "/requests/{request_id}",
    summary="Process request",
    description="Process an approved request by changing its status and "
    "creating a tracking record. Rejecting requires a mandatory "
    "comment. Requests must be in approved status.",
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
    return service.admin_process_request(
        request_id=request_id,
        status_in=status,
        user=current_user,
        comment=comment,
        background_tasks=background_tasks,
    )
