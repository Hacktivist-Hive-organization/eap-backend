# scripts/seed/demo_data_n.py

from sqlalchemy.orm import Session

from app.common.enums import Priority, Status, UserRole
from app.common.security import hash_password
from app.database.session import SessionLocal
from app.models import (
    DBRequest,
    DBRequestSubtype,
    DBRequestTracking,
    DBRequestType,
    DbUser,
)


def seed_demo_data():
    db: Session = SessionLocal()

    # Users
    user1 = db.query(DbUser).filter_by(email="user1@example.com").first()
    user2 = db.query(DbUser).filter_by(email="user2@example.com").first()

    if not user1:
        user1 = DbUser(
            email="user1@example.com",
            first_name="User",
            last_name="One",
            hashed_password=hash_password("Password123!"),
            role=UserRole.REQUESTER,
            is_active=True,
        )
    if not user2:
        user2 = DbUser(
            email="user2@example.com",
            first_name="User",
            last_name="Two",
            hashed_password=hash_password("Password123!"),
            role=UserRole.APPROVER,
            is_active=True,
        )
    db.add_all([user1, user2])
    db.commit()

    # Request types and subtypes
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

    if db.query(DBRequest).count() == 0:
        demo_requests = [
            DBRequest(
                type_id=hardware.id,
                subtype_id=laptop.id,
                title="Request for new development laptop",
                description="Draft request for a new laptop.",
                business_justification="Improve development performance.",
                priority=Priority.HIGH,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=software.id,
                subtype_id=vpn.id,
                title="VPN access for remote work",
                description="Need VPN access to internal systems.",
                business_justification="Required for secure remote access.",
                priority=Priority.MEDIUM,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=services.id,
                subtype_id=training.id,
                title="Backend training course enrollment",
                description="Request to attend advanced backend course.",
                business_justification="Improve system scalability and knowledge.",
                priority=Priority.LOW,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=hardware.id,
                subtype_id=monitor.id,
                title="Additional monitor for workstation",
                description="Second monitor for better multitasking.",
                business_justification="Improves productivity.",
                priority=Priority.MEDIUM,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=software.id,
                subtype_id=software_license.id,
                title="IDE software license",
                description="Professional IDE license request.",
                business_justification="Speeds up development.",
                priority=Priority.LOW,
                requester_id=user1.id,
            ),
        ]
        db.add_all(demo_requests)
        db.commit()

        software_approver = (
            db.query(DbUser).filter_by(email="approver-software@eap.local").first()
        )
        if software_approver:
            tracking = DBRequestTracking(
                status=Status.SUBMITTED,
                user_id=software_approver.id,
                request_id=demo_requests[4].id,
                comment="initial submit",
            )
            demo_requests[4].current_status = Status.SUBMITTED
            db.add(tracking)
            db.commit()

    print("Seeded demo users, requests, and tracking successfully.")
    print("Login credentials:")
    print(" - user1@example.com / Password123!")
    print(" - user2@example.com / Password123!")
