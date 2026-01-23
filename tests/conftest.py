# conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.service_dependency import get_user_service
from app.core import config
from app.database.session import Base, get_db
from app.main import app
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


@pytest.fixture(autouse=True)
def override_settings(monkeypatch):
    monkeypatch.setattr(
        config,
        "settings",
        config.Settings(
            DATABASE_TYPE="sqlite",
            DATABASE_HOST="localhost",
            DATABASE_PORT=5432,
            DATABASE_USER="user",
            DATABASE_PASSWORD="pass",
            DATABASE_NAME="test_db",
            JWT_SECRET_KEY="secret",
        ),
    )


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        future=True,
    )

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    mock_user_repository = UserRepository(db_session)
    mock_user_service = UserService(mock_user_repository)

    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
