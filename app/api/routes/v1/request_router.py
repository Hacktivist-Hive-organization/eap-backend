# app/api/routes/v1/request_router.py

from typing import List

from fastapi import APIRouter, Depends

from app.api.dependencies.service_dependency import get_request_service
from app.api.schemas.request_schema import RequestCreateSchema, RequestResponseSchema

router = APIRouter(tags=["Requests"])


@router.post("/", response_model=RequestResponseSchema)
def create_request(
    request_in: RequestCreateSchema, service=Depends(get_request_service)
):
    request_in.requester_id = 1  # here we should assign the current user id
    return service.create_request(request_in)


@router.get(
    "/my-requests",
    summary="Get all requests by user",
    description="Get all user requests by status order by creation date",
    response_model=List[RequestResponseSchema],
)
def get_requests_by_user(status: str, service=Depends(get_request_service)):
    user_id = 1  # here we should assign the current user id
    return service.get_requests_by_user(user_id, status)
