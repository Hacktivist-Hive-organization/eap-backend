# app/api/routes/v1/request_router.py
from fastapi import APIRouter, Depends
from app.api.schemas.request_schema import (RequestCreateSchema,                                        RequestResponseSchema)
from app.api.dependencies.service_dependency import get_request_service

router = APIRouter(tags=["Requests"])

@router.post("/", response_model=RequestResponseSchema)
def create_request(
    request_in: RequestCreateSchema, service = Depends(get_request_service)
):
    return service.create_request(request_in)
