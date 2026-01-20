from fastapi import APIRouter

from app.api.routes.v1 import router as v1_router
from app.core.config import settings

router = APIRouter(prefix=settings.API_V1_PREFIX)
router.include_router(v1_router)
