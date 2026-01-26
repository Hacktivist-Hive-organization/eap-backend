# app/api/routes/v1/request_type_router.py
from fastapi import APIRouter, Depends,  Query
from typing import List
from app.api.schemas.request_type_schema import RequestTypeResponseSchema
from app.api.dependencies.service_dependency import get_request_type_service

router = APIRouter(tags=["Request Types"])

@router.get("/", response_model=List[RequestTypeResponseSchema])
def get_all_types(service = Depends(get_request_type_service)):
    """
    Return all request types with their nested subtypes.
    """
    return service.get_all()