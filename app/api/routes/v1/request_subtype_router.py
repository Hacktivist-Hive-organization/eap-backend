# app/api/routes/v1/request_subtype_router.py

from fastapi import APIRouter, Depends, Response

from app.api.dependencies.service_dependency import get_request_subtype_service
from app.api.schemas.request_subtype_schema import RequestSubtypeResponseSchema

router = APIRouter(tags=["Request Subtypes"])


@router.get("/", response_model=list[RequestSubtypeResponseSchema])
def get_all_subtypes(response: Response, service=Depends(get_request_subtype_service)):
    return service.get_all()
