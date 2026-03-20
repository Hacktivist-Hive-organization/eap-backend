# scripts/seed/reset_and_seed.py

import sys
from pathlib import Path

# --------------------------
# Setup project root for imports
# --------------------------
BASE_DIR = Path(__file__).resolve()
while not (BASE_DIR / "app").exists():
    BASE_DIR = BASE_DIR.parent

sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import text

# --------------------------
# Imports
# --------------------------
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
from scripts.seed.request_types import seed_request_type_subtype_data
from scripts.seed.users import seed_users


# --------------------------
# Reset database
# --------------------------
def reset_database(db: Session):
    print("Resetting database...")

    tables = [
        "request_tracking",
        "requests",
        "request_type_approver",
        "request_subtype",
        "request_type",
        "users",
    ]

    for table in tables:
        try:
            db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
            print(f"Truncated: {table}")
        except Exception as e:
            db.rollback()  # rollback on failure
            print(f"Skip {table}: {e}")

    db.commit()
    print("Database reset complete")


# --------------------------
# Seed demo data (users + requests)
# --------------------------
def seed_demo_data(db: Session):
    print("Seeding demo data...")

    # --- Demo users ---
    user1_exist = db.query(DbUser).filter_by(email="user1@example.com").first()
    user2_exist = db.query(DbUser).filter_by(email="user2@example.com").first()

    if not user1_exist:
        user1 = DbUser(
            email="user1@example.com",
            first_name="User",
            last_name="One",
            hashed_password=hash_password("Password123!"),
            role=UserRole.REQUESTER,
            is_active=True,
        )
        db.add(user1)
    else:
        user1 = user1_exist

    if not user2_exist:
        user2 = DbUser(
            email="user2@example.com",
            first_name="User",
            last_name="Two",
            hashed_password=hash_password("Password123!"),
            role=UserRole.APPROVER,
            is_active=True,
        )
        db.add(user2)
    else:
        user2 = user2_exist

    db.commit()

    # --- Required approver ---
    software_approver = (
        db.query(DbUser).filter_by(email="approver-software@eap.local").first()
    )
    if not software_approver:
        raise ValueError("Software approver user not found! Must exist in seed_users")

    # --- Request types ---
    hardware = db.query(DBRequestType).filter_by(name="Hardware").first()
    software = db.query(DBRequestType).filter_by(name="Software & Access").first()
    services = db.query(DBRequestType).filter_by(name="Services & Facilities").first()

    # --- Request subtypes ---
    laptop = db.query(DBRequestSubtype).filter_by(name="Laptop").first()
    monitor = db.query(DBRequestSubtype).filter_by(name="Monitor").first()
    vpn = db.query(DBRequestSubtype).filter_by(name="VPN access").first()
    software_license = (
        db.query(DBRequestSubtype).filter_by(name="Software license").first()
    )
    training = (
        db.query(DBRequestSubtype).filter_by(name="Training/course enrollment").first()
    )

    # --- Demo requests ---
    if db.query(DBRequest).count() == 0:
        demo_requests = [
            DBRequest(
                type_id=hardware.id,
                subtype_id=laptop.id,
                title="Request for new development laptop",
                description="Draft request for a new laptop",
                business_justification="Improve performance",
                priority=Priority.HIGH,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=software.id,
                subtype_id=vpn.id,
                title="VPN access",
                description="VPN needed",
                business_justification="Remote work",
                priority=Priority.MEDIUM,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=services.id,
                subtype_id=training.id,
                title="Training request",
                description="Backend course",
                business_justification="Improve skills",
                priority=Priority.LOW,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=hardware.id,
                subtype_id=monitor.id,
                title="Second monitor",
                description="More workspace",
                business_justification="Productivity",
                priority=Priority.MEDIUM,
                requester_id=user1.id,
            ),
            DBRequest(
                type_id=software.id,
                subtype_id=software_license.id,
                title="IDE license",
                description="Better tools",
                business_justification="Speed up dev",
                priority=Priority.LOW,
                requester_id=user1.id,
            ),
        ]

        db.add_all(demo_requests)
        db.commit()

        # --- Initial tracking ---
        tracking = DBRequestTracking(
            status=Status.SUBMITTED,
            user_id=software_approver.id,
            request_id=demo_requests[4].id,
            comment="initial submit",
        )

        demo_requests[4].current_status = Status.SUBMITTED

        db.add(tracking)
        db.commit()

    print("Demo data seeded successfully")
    print("Login credentials:")
    print(" - user1@example.com / Password123!")
    print(" - user2@example.com / Password123!")


# --------------------------
# Run all seeds
# --------------------------
def run_seed(db: Session):
    print("Seeding base data...")

    seed_users(db)
    seed_request_type_subtype_data(db)
    seed_demo_data(db)

    print("All seeding complete")


# --------------------------
# Main
# --------------------------
def main():
    db: Session = SessionLocal()

    try:
        reset_database(db)
        run_seed(db)
        print("\n✅ Reset and seed finished successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
