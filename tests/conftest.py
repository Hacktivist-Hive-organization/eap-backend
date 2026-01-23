# tests/conftest.py

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base, get_db
from app.main import app as main_app


@pytest.fixture(scope="session")
def sqlite_connection():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    connection = engine.connect()
    Base.metadata.create_all(bind=connection)
    yield connection
    Base.metadata.drop_all(bind=connection)
    connection.close()


@pytest.fixture(scope="function")
def db_session(sqlite_connection):
    TestingSessionLocal = sessionmaker(
        bind=sqlite_connection,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    # создаём **новое приложение**, копию main_app без lifespan
    app = FastAPI(title=main_app.title, version=main_app.version)
    app.include_router(main_app.router)
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client
