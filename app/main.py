from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes.routes import router
from app.core.config import settings
from app.database.session import create_tables, drop_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    # application execution
    yield

    # application shutdown

app = FastAPI(title=settings.APP_NAME,
    version=settings.APP_VERSION,lifespan=lifespan)
app.include_router(router)
