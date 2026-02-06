# confest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import get_user_service
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from tests.integration.helpers import seed_types_and_subtypes, seed_user


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)
    session = testing_session_local()

    try:
        yield session
    finally:
        session.close()

        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    user_repository = UserRepository(db_session)
    user_service = UserService(user_repository)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_service] = lambda: user_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def users(db_session):
    users = seed_user(db_session)
    return users


@pytest.fixture(scope="function")
def seeded_request_types(db_session):
    """
    Seeds request types and subtypes.
    Returns a dict like:
    {
        "hardware": <DbRequestType>,
        "software": <DbRequestType>,
        "laptop": <DbRequestSubtype>,
        "license": <DbRequestSubtype>,
    }
    """
    return seed_types_and_subtypes(db_session)


@pytest.fixture
def auth_as():
    def _auth(user):
        app.dependency_overrides[get_current_user] = lambda: user

    yield _auth
    app.dependency_overrides.clear()
