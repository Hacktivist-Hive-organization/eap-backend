# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import get_email_manager, get_user_service
from app.core.config import settings
from app.database.base import Base
from app.database.session import get_db
from app.infrastructure.email.manager import EmailManager
from app.main import app
from app.models import DBRequest
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from tests.integration.helpers import (
    seed_admins,
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
    TestingSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
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
        try:
            yield db_session
        finally:
            pass

    user_repo = UserRepository(db_session)
    user_service = UserService(user_repo)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_user_service] = lambda: user_service
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def users(db_session):
    return seed_user(db_session)


@pytest.fixture
def dashboard_admin(db_session):
    return seed_admins(db_session)


@pytest.fixture
def dashboard_approvers(db_session):
    return seed_dashboard_approvers(db_session)


@pytest.fixture(scope="function")
def seeded_request_types(db_session):
    return seed_types_and_subtypes(db_session)


@pytest.fixture
def auth_as():
    def _auth(user):
        app.dependency_overrides[get_current_user] = lambda: user

    yield _auth
    app.dependency_overrides.clear()


@pytest.fixture
def valid_request_payload(seeded_request_types):
    def _factory(title="Default Title", current_status=None):
        data = seeded_request_types

        return {
            "type_id": data["hardware"].id,
            "subtype_id": data["laptop"].id,
            "title": title,
            "description": "This is a valid description with at least 20 chars",
            "business_justification": "Business justification is long enough for validation",
            "priority": "medium",
            "current_status": current_status.value if current_status else "draft",
        }

    return _factory


@pytest.fixture
def seeded_requests_for_user(db_session, users, seeded_request_types):
    from app.common.enums import Priority, Status

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


@pytest.fixture(autouse=True)
def real_email_manager():
    settings.EMAIL_SERVICE = getattr(settings, "EMAIL_SERVICE", "mailtrap")
    email_manager = EmailManager()
    app.dependency_overrides[get_email_manager] = lambda: email_manager
    yield
    app.dependency_overrides.clear()
