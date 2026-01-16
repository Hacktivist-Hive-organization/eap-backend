from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes.routes import router
from app.core.config import settings
from app.database.session import create_tables
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    # application execution
    yield

    # application shutdown

app = FastAPI(title=settings.APP_NAME,
    version=settings.APP_VERSION,lifespan=lifespan)

if settings.MIDDLEWARE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

app.include_router(router)
