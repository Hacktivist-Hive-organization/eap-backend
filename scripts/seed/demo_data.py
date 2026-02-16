# demo_data.py

from app.common.enums import Priority, Status, UserRole
from app.common.security import hash_password
from app.database.session import SessionLocal
from app.models import DbUser
from app.models.db_request import DBRequest
from app.models.db_request_subtype import DBRequestSubtype
from app.models.db_request_type import DBRequestType


def seed_demo_data():
    db = SessionLocal()
    # -----------------------
    # Demo user
    # -----------------------
    if db.query(DbUser).filter(DbUser.email == "user1@example.com").count() > 0:
        return

    user1 = DbUser(
        email="user1@example.com",
        first_name="User",
        last_name="One",
        hashed_password=hash_password("user123!"),
        is_active=True,
    )

    db.add_all([user1])
    db.commit()

    # -----------------------
    # Demo requests
    # -----------------------

    hardware = db.query(DBRequestType).filter_by(name="Hardware").first()
    software = db.query(DBRequestType).filter_by(name="Software & Access").first()
    services = db.query(DBRequestType).filter_by(name="Services & Facilities").first()

    laptop = db.query(DBRequestSubtype).filter_by(name="Laptop").first()
    monitor = db.query(DBRequestSubtype).filter_by(name="Monitor").first()
    vpn = db.query(DBRequestSubtype).filter_by(name="VPN access").first()
    software_license = (
        db.query(DBRequestSubtype).filter_by(name="Software license").first()
    )
    training = (
        db.query(DBRequestSubtype).filter_by(name="Training/course enrollment").first()
    )

    demo_requests = [
        # Drafts (3)
        DBRequest(
            type_id=hardware.id,
            subtype_id=laptop.id,
            title="Request for new development laptop",
            description="Draft request for a new laptop to support development work.",
            business_justification="Will improve development performance and reliability.",
            priority=Priority.HIGH,
            current_status=Status.DRAFT,
            requester_id=user1.id,
        ),
        DBRequest(
            type_id=hardware.id,
            subtype_id=monitor.id,
            title="Additional monitor for workstation",
            description="Considering a second monitor for better multitasking.",
            business_justification="Improves productivity during development and reviews.",
            priority=Priority.MEDIUM,
            current_status=Status.DRAFT,
            requester_id=user1.id,
        ),
        DBRequest(
            type_id=software.id,
            subtype_id=software_license.id,
            title="IDE software license",
            description="Draft request for a professional IDE license.",
            business_justification="Advanced tooling speeds up development and debugging.",
            priority=Priority.LOW,
            current_status=Status.DRAFT,
            requester_id=user1.id,
        ),
        # Submitted / non-draft (2)
        DBRequest(
            type_id=software.id,
            subtype_id=vpn.id,
            title="VPN access for remote work",
            description="Need VPN access to securely connect to internal systems.",
            business_justification="Required for secure remote access.",
            priority=Priority.MEDIUM,
            current_status=Status.SUBMITTED,
            requester_id=user1.id,
        ),
        DBRequest(
            type_id=services.id,
            subtype_id=training.id,
            title="Backend training course enrollment",
            description="Request to attend an advanced backend architecture course.",
            business_justification="Improves system scalability and team knowledge.",
            priority=Priority.LOW,
            current_status=Status.SUBMITTED,
            requester_id=user1.id,
        ),
    ]

    db.add_all(demo_requests)
    db.commit()
