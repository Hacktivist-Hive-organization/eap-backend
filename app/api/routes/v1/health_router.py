# app/api/routes/v1/health_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies.service_dependency import get_health_service
from app.services.health_service import HealthService

router = APIRouter(prefix="", tags=["health"])


@router.get(
    "/",
    include_in_schema=False,
)
def health_check(service: HealthService = Depends(get_health_service)):
    try:
        db_status = service.get_health()
    except SQLAlchemyError:
        db_status = "disconnected"

    return {"status": "ok", "database": db_status}
