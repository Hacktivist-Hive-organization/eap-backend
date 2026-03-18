# app/api/routes/v1/__init__.py

from fastapi import APIRouter

from app.api.routes.v1.auth_router import router as auth_router
from app.api.routes.v1.email_router import router as email_router
from app.api.routes.v1.health_router import router as health_router
from app.api.routes.v1.request_router import router as request_router
from app.api.routes.v1.request_subtype_router import router as subtype_router
from app.api.routes.v1.request_tracking_router import router as tracking_router
from app.api.routes.v1.request_type_router import router as type_router
from app.api.routes.v1.user_router import router as user_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(user_router, prefix="/users")

router.include_router(request_router, prefix="/requests")
router.include_router(tracking_router, prefix="/tracking")

router.include_router(type_router, prefix="/types")
router.include_router(subtype_router, prefix="/subtypes")


router.include_router(health_router, prefix="/health")
router.include_router(email_router, prefix="/email")
