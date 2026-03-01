# tests/conftest.py
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import (
    get_auth_service,
    get_email_manager,
    get_user_service,
)
from app.common.enums import Priority, Status
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.models import DBRequest
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from tests.integration.helpers import (
    seed_dashboard_approvers,
    seed_types_and_subtypes,
    seed_user,
)


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


@pytest.fixture
def dashboard_approvers(db_session):
    return seed_dashboard_approvers(db_session)


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


@pytest.fixture
def valid_request_payload(seeded_request_types):
    """
    Returns a factory function to generate valid request payloads.
    Usage:
        payload = valid_request_payload(title="My Request", status=Status.DRAFT)
    """

    def _factory(title="Default Title", current_status=Status.DRAFT):
        data = seeded_request_types
        return {
            "type_id": data["hardware"].id,
            "subtype_id": data["laptop"].id,
            "title": title,
            "description": "This is a valid description with at least 20 chars",
            "business_justification": "Business justification is long enough for validation",
            "priority": "medium",
            "current_status": current_status.value,
        }

    return _factory


@pytest.fixture
def seeded_requests_for_user(db_session, users, seeded_request_types):
    """
    Seeds multiple requests with different statuses
    for user1. Returns created requests.
    """

    owner = users["user1"]
    data = seeded_request_types

    requests = [
        DBRequest(
            type_id=data["hardware"].id,
            subtype_id=data["laptop"].id,
            title="Draft Req",
            description="Valid description long enough",
            business_justification="Valid justification long enough",
            priority=Priority.MEDIUM,
            current_status=Status.DRAFT,
            requester_id=owner.id,
        ),
        DBRequest(
            type_id=data["hardware"].id,
            subtype_id=data["laptop"].id,
            title="Submitted Req",
            description="Valid description long enough",
            business_justification="Valid justification long enough",
            priority=Priority.MEDIUM,
            current_status=Status.SUBMITTED,
            requester_id=owner.id,
        ),
        # APPROVED
        DBRequest(
            type_id=data["hardware"].id,
            subtype_id=data["laptop"].id,
            title="Approved Req",
            description="Valid description long enough",
            business_justification="Valid justification long enough",
            priority=Priority.MEDIUM,
            current_status=Status.APPROVED,
            requester_id=owner.id,
        ),
        DBRequest(
            type_id=data["hardware"].id,
            subtype_id=data["laptop"].id,
            title="Approved Req 2",
            description="Valid description long enough",
            business_justification="Valid justification long enough",
            priority=Priority.MEDIUM,
            current_status=Status.APPROVED,
            requester_id=owner.id,
        ),
        # REJECTED
        DBRequest(
            type_id=data["hardware"].id,
            subtype_id=data["laptop"].id,
            title="Rejected Req",
            description="Valid description long enough",
            business_justification="Valid justification long enough",
            priority=Priority.MEDIUM,
            current_status=Status.REJECTED,
            requester_id=owner.id,
        ),
    ]

    db_session.add_all(requests)
    db_session.commit()

    return requests
