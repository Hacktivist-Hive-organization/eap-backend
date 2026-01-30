from app.models import DbUser
from app.models.db_request import DBRequest
from app.models.db_request_subtype import DBRequestSubtype
from app.models.db_request_type import DBRequestType
from app.common.enums import Priority, Status


def seed_request_data(db):
    # Prevent reseeding
    if db.query(DBRequestType).count() > 0:
        return

    # -----------------------
    # Request types
    # -----------------------
    hardware = DBRequestType(name="Hardware")
    software = DBRequestType(name="Software & Access")
    services = DBRequestType(name="Services & Facilities")

    # -----------------------
    # Demo user
    # -----------------------
    user1 = DbUser(
        email="user1@example.com",
        first_name="User",
        last_name="One",
        hashed_password="not_a_real_hash",  # replace if needed
        is_active=True,
    )

    db.add_all([hardware, software, services, user1])
    db.commit()

    # -----------------------
    # Subtypes
    # -----------------------
    subtypes = [
        # Hardware
        DBRequestSubtype(name="Laptop", type_id=hardware.id),
        DBRequestSubtype(name="Desktop", type_id=hardware.id),
        DBRequestSubtype(name="Monitor", type_id=hardware.id),
        DBRequestSubtype(name="Peripherals", type_id=hardware.id),
        DBRequestSubtype(name="Mobile device", type_id=hardware.id),
        DBRequestSubtype(name="Other", type_id=hardware.id),

        # Software
        DBRequestSubtype(name="Software license", type_id=software.id),
        DBRequestSubtype(name="System access", type_id=software.id),
        DBRequestSubtype(name="Application access", type_id=software.id),
        DBRequestSubtype(name="VPN access", type_id=software.id),
        DBRequestSubtype(name="Other", type_id=software.id),

        # Services
        DBRequestSubtype(name="Parking spot", type_id=services.id),
        DBRequestSubtype(name="Office equipment", type_id=services.id),
        DBRequestSubtype(name="Training/course enrollment", type_id=services.id),
        DBRequestSubtype(name="Travel approval", type_id=services.id),
        DBRequestSubtype(name="Other", type_id=services.id),
    ]

    db.add_all(subtypes)
    db.commit()

    # -----------------------
    # Demo requests
    # -----------------------
    laptop = next(s for s in subtypes if s.name == "Laptop")
    monitor = next(s for s in subtypes if s.name == "Monitor")
    vpn = next(s for s in subtypes if s.name == "VPN access")
    software_license = next(s for s in subtypes if s.name == "Software license")
    training = next(s for s in subtypes if s.name == "Training/course enrollment")

    demo_requests = [
        # Drafts (3)
        DBRequest(
            type_id=hardware.id,
            subtype_id=laptop.id,
            title="Request for new development laptop",
            description="Draft request for a new laptop to support development work.",
            business_justification="Will improve development performance and reliability.",
            priority=Priority.HIGH,
            status=Status.DRAFT,
            requester_id=user1.id,
        ),
        DBRequest(
            type_id=hardware.id,
            subtype_id=monitor.id,
            title="Additional monitor for workstation",
            description="Considering a second monitor for better multitasking.",
            business_justification="Improves productivity during development and reviews.",
            priority=Priority.MEDIUM,
            status=Status.DRAFT,
            requester_id=user1.id,
        ),
        DBRequest(
            type_id=software.id,
            subtype_id=software_license.id,
            title="IDE software license",
            description="Draft request for a professional IDE license.",
            business_justification="Advanced tooling speeds up development and debugging.",
            priority=Priority.LOW,
            status=Status.DRAFT,
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
            status=Status.SUBMITTED,
            requester_id=user1.id,
        ),
        DBRequest(
            type_id=services.id,
            subtype_id=training.id,
            title="Backend training course enrollment",
            description="Request to attend an advanced backend architecture course.",
            business_justification="Improves system scalability and team knowledge.",
            priority=Priority.LOW,
            status=Status.SUBMITTED,
            requester_id=user1.id,
        ),
    ]

    db.add_all(demo_requests)
    db.commit()
