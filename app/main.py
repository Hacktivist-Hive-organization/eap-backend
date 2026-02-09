# main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.routes import router
from app.common.exception_handlers import (
    business_exception_handler,
    validation_exception_handler,
)
from app.common.exceptions import BusinessException
from app.core.config import settings
from scripts.seed.demo_data import seed_demo_data
from scripts.seed.run import run_seeds


@asynccontextmanager
async def lifespan(app: FastAPI):

    if settings.DEVELOPMENT_ENVIRONMENT:
        run_seeds()
        seed_demo_data()
    yield

    # application shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    swagger_ui_parameters={"docExpansion": "none"},
)

if settings.MIDDLEWARE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(router)

# Register handlers
app.add_exception_handler(
    BusinessException,
    business_exception_handler,
)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)
