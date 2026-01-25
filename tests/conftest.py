import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.service_dependency import get_user_service
from app.core.config import settings
from app.database.session import Base, get_db
from app.main import app as fastapi_app
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

# Automatically use test environment
os.environ["ENV_FILE"] = ".env.test"

engine = create_engine(
    f"sqlite+pysqlite:///{settings.DATABASE_NAME}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    user_repository = UserRepository(db_session)
    user_service = UserService(user_repository)

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[get_user_service] = lambda: user_service

    with TestClient(fastapi_app) as test_client:
        yield test_client

    fastapi_app.dependency_overrides.clear()
