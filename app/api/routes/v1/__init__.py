from fastapi import APIRouter
from app.api.routes.v1.user import router as user_router
from app.api.routes.v1.health import router as health_router


router = APIRouter()

router.include_router(user_router, prefix='/user')
router.include_router(health_router, prefix='/health')

