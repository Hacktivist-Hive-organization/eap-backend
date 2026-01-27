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
from app.database.seed_request_data import seed_request_data
from app.database.session import create_tables, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    # application execution
    db = next(get_db())
    seed_request_data(db)
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
