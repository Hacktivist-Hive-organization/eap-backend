# demo_data_full.py

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

# -----------------------
# Configure which statuses to include
# -----------------------
ENABLED_STATUSES = {
    Status.DRAFT,
    Status.SUBMITTED,
    Status.APPROVED,
    Status.IN_PROGRESS,
    Status.CANCELLED,
    Status.REJECTED,
}


def seed_demo_data():
    db = SessionLocal()

    # -----------------------
    # Users
    # -----------------------
    user1 = db.query(DbUser).filter_by(email="user1@example.com").first()
    if not user1:
        user1 = DbUser(
            email="user1@example.com",
            first_name="User",
            last_name="One",
            hashed_password=hash_password("Password123!"),
            role=UserRole.REQUESTER,
            is_active=True,
        )
        db.add(user1)

    user2 = db.query(DbUser).filter_by(email="user2@example.com").first()
    if not user2:
        user2 = DbUser(
            email="user2@example.com",
            first_name="User",
            last_name="Two",
            hashed_password=hash_password("Password123!"),
            role=UserRole.APPROVER,
            is_active=True,
        )
        db.add(user2)

    user3 = DbUser(
        email="requester-1@eap.local",
        first_name="Requester1",
        last_name="Requester",
        hashed_password=hash_password("Password123!"),
        role=UserRole.REQUESTER,
        is_active=True,
    )
    db.add(user3)

    user4 = DbUser(
        email="requester-2@eap.local",
        first_name="Requester2",
        last_name="Requester",
        hashed_password=hash_password("Password123!"),
        role=UserRole.REQUESTER,
        is_active=True,
    )
    db.add(user4)

    db.commit()

    # -----------------------
    # Required approver
    # -----------------------
    software_approver = (
        db.query(DbUser).filter_by(email="approver-software@eap.local").first()
    )
    if not software_approver:
        raise ValueError("Software approver user not found")

    # -----------------------
    # Request types and subtypes
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

    # -----------------------
    # Request templates
    # -----------------------
    all_templates = [
        dict(
            status=Status.DRAFT,
            type_id=hardware.id,
            subtype_id=laptop.id,
            title="Draft laptop request",
            priority=Priority.MEDIUM,
        ),
        dict(
            status=Status.DRAFT,
            type_id=software.id,
            subtype_id=vpn.id,
            title="Draft VPN request",
            priority=Priority.LOW,
        ),
        dict(
            status=Status.DRAFT,
            type_id=services.id,
            subtype_id=training.id,
            title="Draft training request",
            priority=Priority.LOW,
        ),
        dict(
            status=Status.SUBMITTED,
            type_id=hardware.id,
            subtype_id=laptop.id,
            title="QA laptop request",
            priority=Priority.MEDIUM,
        ),
        dict(
            status=Status.SUBMITTED,
            type_id=software.id,
            subtype_id=vpn.id,
            title="Contractor VPN request",
            priority=Priority.HIGH,
        ),
        dict(
            status=Status.SUBMITTED,
            type_id=services.id,
            subtype_id=training.id,
            title="DevOps training request",
            priority=Priority.LOW,
        ),
        dict(
            status=Status.APPROVED,
            type_id=hardware.id,
            subtype_id=monitor.id,
            title="Monitor upgrade request",
            priority=Priority.LOW,
        ),
        dict(
            status=Status.APPROVED,
            type_id=software.id,
            subtype_id=software_license.id,
            title="DB tool license request",
            priority=Priority.MEDIUM,
        ),
        dict(
            status=Status.APPROVED,
            type_id=services.id,
            subtype_id=training.id,
            title="Leadership training request",
            priority=Priority.LOW,
        ),
        dict(
            status=Status.IN_PROGRESS,
            type_id=hardware.id,
            subtype_id=laptop.id,
            title="Designer laptop request",
            priority=Priority.HIGH,
        ),
        dict(
            status=Status.IN_PROGRESS,
            type_id=software.id,
            subtype_id=vpn.id,
            title="VPN upgrade request",
            priority=Priority.MEDIUM,
        ),
        dict(
            status=Status.IN_PROGRESS,
            type_id=services.id,
            subtype_id=training.id,
            title="Cloud certification request",
            priority=Priority.HIGH,
        ),
        dict(
            status=Status.CANCELLED,
            type_id=hardware.id,
            subtype_id=monitor.id,
            title="Cancelled monitor request",
            priority=Priority.LOW,
        ),
        dict(
            status=Status.CANCELLED,
            type_id=software.id,
            subtype_id=software_license.id,
            title="Cancelled license request",
            priority=Priority.MEDIUM,
        ),
        dict(
            status=Status.CANCELLED,
            type_id=services.id,
            subtype_id=training.id,
            title="Cancelled training request",
            priority=Priority.LOW,
        ),
        dict(
            status=Status.REJECTED,
            type_id=hardware.id,
            subtype_id=laptop.id,
            title="Rejected laptop request",
            priority=Priority.MEDIUM,
        ),
        dict(
            status=Status.REJECTED,
            type_id=software.id,
            subtype_id=software_license.id,
            title="Rejected license request",
            priority=Priority.MEDIUM,
        ),
        dict(
            status=Status.REJECTED,
            type_id=services.id,
            subtype_id=training.id,
            title="Rejected training request",
            priority=Priority.LOW,
        ),
    ]

    # -----------------------
    # Filter templates by ENABLED_STATUSES
    # -----------------------
    request_templates = [t for t in all_templates if t["status"] in ENABLED_STATUSES]

    demo_requests = []
    demo_tracking = []

    # -----------------------
    # Create requests
    # -----------------------
    for t in request_templates:
        req = DBRequest(
            type_id=t["type_id"],
            subtype_id=t["subtype_id"],
            title=t["title"],
            description=f"Auto-generated request: {t['title']}",
            business_justification="Auto-generated",
            priority=t["priority"],
            requester_id=user1.id,
            current_status=t["status"],
        )
        demo_requests.append(req)

    db.add_all(demo_requests)
    db.commit()

    # -----------------------
    # Create tracking (skip draft)
    # -----------------------
    for req, t in zip(demo_requests, request_templates):
        if t["status"] == Status.DRAFT:
            continue
        demo_tracking.append(
            DBRequestTracking(
                status=t["status"],
                user_id=software_approver.id,
                request_id=req.id,
                comment="processed",
            )
        )

    db.add_all(demo_tracking)
    db.commit()

    print("Seeded demo data successfully")
    print("Login credentials:")
    print(" - user1@example.com / Password123!")
    print(" - user2@example.com / Password123!")
