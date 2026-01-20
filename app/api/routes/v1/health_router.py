from fastapi import Depends, APIRouter

from app.api.dependencies.service_dependency import get_health_service
from app.services.health_service import HealthService

router = APIRouter(prefix="", tags=["health"])

@router.get("/")
def health_check(service: HealthService = Depends(get_health_service)):
    try:
        db_status= service.get_health()
    except Exception:
        db_status= "disconnected"

    return {
        "status": "ok",
        "database": db_status
    }