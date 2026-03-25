# scripts/seed/users.py

from sqlalchemy.orm import Session

from app.common.enums import UserRole
from app.common.security import hash_password
from app.models.db_user import DbUser


def seed_users(db: Session):
    if db.query(DbUser).count() > 0:
        return

    admin = DbUser(
        email="admin@eap.local",
        first_name="System",
        last_name="Admin",
        hashed_password=hash_password("Password123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    admin_2 = DbUser(
        email="admin2@eap.local",
        first_name="System",
        last_name="Admin",
        hashed_password=hash_password("Password123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )

    approver_hardware = DbUser(
        email="approver-hardware@eap.local",
        first_name="Hardware",
        last_name="Approver",
        hashed_password=hash_password("Password123!"),
        role=UserRole.APPROVER,
        is_active=True,
    )
    approver_hardware_2 = DbUser(
        email="approver-hardware-2@eap.local",
        first_name="Hardware",
        last_name="Approver",
        hashed_password=hash_password("Password123!"),
        role=UserRole.APPROVER,
        is_active=True,
    )

    approver_software = DbUser(
        email="approver-software@eap.local",
        first_name="Software",
        last_name="Approver",
        hashed_password=hash_password("Password123!"),
        role=UserRole.APPROVER,
        is_active=True,
    )

    approver_software_2 = DbUser(
        email="approver-software-2@eap.local",
        first_name="Software",
        last_name="Approver",
        hashed_password=hash_password("Password123!"),
        role=UserRole.APPROVER,
        is_active=True,
    )

    approver_services = DbUser(
        email="approver-services@eap.local",
        first_name="Services",
        last_name="Approver",
        hashed_password=hash_password("Password123!"),
        role=UserRole.APPROVER,
        is_active=True,
    )

    approver_services_2 = DbUser(
        email="approver-services-2@eap.local",
        first_name="Services",
        last_name="Approver",
        hashed_password=hash_password("Password123!"),
        role=UserRole.APPROVER,
        is_active=True,
    )

    requester = DbUser(
        email="requester@eap.local",
        first_name="System",
        last_name="Admin",
        hashed_password=hash_password("Password123!"),
        role=UserRole.REQUESTER,
        is_active=True,
    )

    requester_2 = DbUser(
        email="requester-2@eap.local",
        first_name="System",
        last_name="Admin",
        hashed_password=hash_password("Password123!"),
        role=UserRole.REQUESTER,
        is_active=True,
    )

    db.add_all(
        [
            admin,
            admin_2,
            approver_hardware,
            approver_hardware_2,
            approver_software,
            approver_software_2,
            approver_services,
            approver_services_2,
            requester,
            requester_2,
        ]
    )
    db.commit()
