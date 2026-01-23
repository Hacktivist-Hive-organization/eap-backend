from fastapi import APIRouter
from app.api.routes.v1.health import router as health_router
from app.api.routes.v1.request_router import router as request_router
from app.api.routes.v1.user import router as user_router
from app.api.routes.v1.request_type_router import router as type_router
from app.api.routes.v1.request_subtype_router import router as subtype_router
router = APIRouter()

router.include_router(user_router, prefix="/user")
router.include_router(health_router, prefix="/health")
router.include_router(request_router, prefix="/requests")
router.include_router(type_router, prefix="/types")
router.include_router(subtype_router, prefix="/subtypes")