# demo_data.py
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
    db = SessionLocal()

    # -----------------------
    # Demo user
    # -----------------------
    if db.query(DbUser).filter(DbUser.email == "user1@example.com").count() == 0:
        user1 = DbUser(
            email="user1@example.com",
            first_name="User",
            last_name="One",
            hashed_password=hash_password("Password123!"),
            role=UserRole.REQUESTER,
            is_active=True,
        )
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
    else:
        user1 = db.query(DbUser).filter(DbUser.email == "user1@example.com").first()
        user2 = db.query(DbUser).filter(DbUser.email == "user2@example.com").first()

    # -----------------------
    # Demo requests
    # -----------------------
    software_approver = (
        db.query(DbUser).filter_by(email="approver-software@eap.local").first()
    )
    if not software_approver:
        raise ValueError("Software approver user not found")

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
                description="Draft request for a new laptop to support development work.",
                business_justification="Will improve development performance and reliability.",
                priority=Priority.HIGH,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=software.id,
                subtype_id=vpn.id,
                title="VPN access for remote work",
                description="Need VPN access to securely connect to internal systems.",
                business_justification="Required for secure remote access.",
                priority=Priority.MEDIUM,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=services.id,
                subtype_id=training.id,
                title="Backend training course enrollment",
                description="Request to attend an advanced backend architecture course.",
                business_justification="Improves system scalability and team knowledge.",
                priority=Priority.LOW,
                requester_id=user1.id,
            ),
            # Approved
            DBRequest(
                type_id=hardware.id,
                subtype_id=monitor.id,
                title="Additional monitor for workstation",
                description="Considering a second monitor for better multitasking.",
                business_justification="Improves productivity during development and reviews.",
                priority=Priority.MEDIUM,
                requester_id=user1.id,
            ),
            # Rejected
            DBRequest(
                type_id=software.id,
                subtype_id=software_license.id,
                title="IDE software license",
                description="Draft request for a professional IDE license.",
                business_justification="Advanced tooling speeds up development and debugging.",
                priority=Priority.LOW,
                requester_id=user1.id,
            ),
        ]
        db.add_all(demo_requests)
        db.commit()

        if db.query(DBRequestTracking).count() == 0:
            demo_tracking_requests = [
                # Draft
                DBRequestTracking(
                    status=Status.SUBMITTED,
                    user_id=software_approver.id,
                    request_id=demo_requests[4].id,
                    comment="initial submit",
                ),
            ]

            demo_requests[4].current_status = Status.SUBMITTED

            db.add_all(demo_tracking_requests)
            db.commit()

    print("Seeded demo users, request types, subtypes, and requests successfully.")
    print("User credentials for login:")
    print(" - Email: user1@example.com / Password: Password123!")
    print(" - Email: user2@example.com / Password: Password123!")
