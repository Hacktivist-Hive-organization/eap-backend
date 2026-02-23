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
        hashed_password=hash_password("admin123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )

    approvers = []
    for rt_name in ["Hardware", "Software & Access", "Services & Facilities"]:
        for i in range(1, 3):  # 2 approvers per type
            approvers.append(
                DbUser(
                    email=f"approver-{rt_name.lower().replace(' ', '-')}-{i}@eap.local",
                    first_name=f"{rt_name} Approver {i}",
                    last_name="User",
                    hashed_password=hash_password("approver123!"),
                    role=UserRole.APPROVER,
                    is_active=True,
                )
            )

    db.add(admin)
    db.add_all(approvers)
    db.commit()
