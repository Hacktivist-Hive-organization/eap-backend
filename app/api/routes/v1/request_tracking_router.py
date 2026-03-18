# app/api/routes/v1/request_tracking_router.py

from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import get_request_tracking_service
from app.api.schemas.request_tracking_schema import RequestTrackingResponseSchema
from app.common.security_models import CurrentUser

router = APIRouter(tags=["Request tracking"])


@router.get(
    "/{id}",
    summary="Retrieve request tracking for specific request",
    description="""
Returns all tracking records for a specific request.

Tracking records are created only after a request is submitted and assigned to an approver. 
Draft requests do not have any tracking history.

**Access is restricted to:**
- The requester who created the request
- The assigned approver
- Users with the ADMIN role
""",
    response_model=List[RequestTrackingResponseSchema],
)
def get_request_tracking_by_request_id(
    id: int,
    service=Depends(get_request_tracking_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_request_tracking_by_request_id(id, current_user)
