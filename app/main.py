# app/main.py

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.middlewares.http_logging_middleware import HttpLoggingMiddleware
from app.api.routes.routes import router
from app.common.exception_handlers import (
    business_exception_handler,
    configuration_exception_handler,
    external_service_exception_handler,
    validation_exception_handler,
)
from app.common.exceptions import (
    BusinessException,
    ConfigurationException,
    ExternalServiceException,
)
from app.core.config import settings
from app.core.logging_config import configure_logging
from scripts.seed.demo_data import seed_demo_data
from scripts.seed.run import run_seeds

configure_logging()


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
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(HttpLoggingMiddleware)

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

app.add_exception_handler(
    ConfigurationException,
    configuration_exception_handler,
)

app.add_exception_handler(
    ExternalServiceException,
    external_service_exception_handler,
)

BASE_DIR = Path(__file__).resolve().parents[1]
images_dir = BASE_DIR / "images"
images_dir.mkdir(exist_ok=True)  # ensure it exists
app.mount("/images", StaticFiles(directory=images_dir), name="images")
