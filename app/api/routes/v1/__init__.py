from fastapi import APIRouter

from app.api.routes.v1.user_router import router as user_router
from app.api.routes.v1.health_router import router as health_router
from app.api.routes.v1.auth_router import router as auth_router

router = APIRouter()

router.include_router(user_router, prefix='/user')
router.include_router(health_router, prefix='/health')
router.include_router(auth_router, prefix='/auth')