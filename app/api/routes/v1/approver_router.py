# app/api/routes/v1/approver_router.py

from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import (
    get_request_tracking_service,
)
from app.api.schemas.request_schema import (
    RequestResponseListSchema,
    RequestResponseSchema,
)
from app.common.enums import Status
from app.common.security_models import CurrentUser

router = APIRouter(tags=["Approver"])


@router.get(
    "/requests",
    summary="Get requests assigned to the current approver",
    description="Returns all requests that are assigned to the logged-in approver. "
    "The optional `statuses` query parameter can be used to filter requests "
    "by their current status. Only users with the APPROVER role can "
    "access this endpoint.",
    response_model=list[RequestResponseListSchema],
)
def approve_request(
    statuses: Optional[List[Status]] = Query(None, description="Filter by statuses"),
    service=Depends(get_request_tracking_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_requests_for_approver(
        current_user=current_user, statuses=statuses
    )


@router.get(
    "/requests/{request_id}",
    summary="Get request details for the current approver",
    description="Returns full details of a request assigned to the logged-in approver.",
    response_model=RequestResponseSchema,
)
def get_approver_request_details(
    request_id: int,
    service=Depends(get_request_tracking_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_request_by_id_for_approver(request_id, current_user.id)
