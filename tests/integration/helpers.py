# tests/integration/helpers.py

from app.models import (
    DBRequestSubtype,
    DBRequestType,
    DBRequestTypeApprover,
    DbUser,
)


def seed_types_and_subtypes(db):
    # -----------------------------
    # Create request types
    # -----------------------------
    hardware = DBRequestType(name="Hardware")
    software = DBRequestType(name="Software")

    db.add_all([hardware, software])
    db.flush()

    # -----------------------------
    # Create subtypes
    # -----------------------------
    laptop = DBRequestSubtype(name="Laptop", type_id=hardware.id)
    desktop = DBRequestSubtype(name="Desktop", type_id=hardware.id)
    license = DBRequestSubtype(name="License", type_id=software.id)

    db.add_all([laptop, desktop, license])
    db.flush()

    # -----------------------------
    # Create approvers
    # -----------------------------
    approver1 = DbUser(
        email="approver1@example.com",
        first_name="Approver",
        last_name="One",
        hashed_password="not_a_real_hash",
        is_active=True,
    )

    approver2 = DbUser(
        email="approver2@example.com",
        first_name="Approver",
        last_name="Two",
        hashed_password="not_a_real_hash",
        is_active=True,
    )

    approver3 = DbUser(
        email="approver3@example.com",
        first_name="Approver",
        last_name="Three",
        hashed_password="not_a_real_hash",
        is_active=True,
    )

    db.add_all([approver1, approver2, approver3])
    db.flush()

    # -----------------------------
    # Assign approvers to types
    # -----------------------------
    db.add_all(
        [
            # 🔥 Hardware → TWO approvers (different workload)
            DBRequestTypeApprover(
                user_id=approver1.id,
                request_type_id=hardware.id,
                workload=5,  # higher workload
            ),
            DBRequestTypeApprover(
                user_id=approver2.id,
                request_type_id=hardware.id,
                workload=1,  # lower workload (should be selected)
            ),
            # Software → single approver (optional)
            DBRequestTypeApprover(
                user_id=approver3.id,
                request_type_id=software.id,
                workload=0,
            ),
        ]
    )

    db.commit()

    return {
        "hardware": hardware,
        "software": software,
        "laptop": laptop,
        "desktop": desktop,
        "license": license,
        "approver1": approver1,  # hardware high workload
        "approver2": approver2,  # hardware low workload
        "approver3": approver3,  # software approver
    }


def seed_user(db):
    user1 = DbUser(
        email="user1@example.com",
        first_name="User",
        last_name="One",
        hashed_password="not_a_real_hash",
        is_active=True,
    )

    user2 = DbUser(
        email="user2@example.com",
        first_name="User",
        last_name="Two",
        hashed_password="not_a_real_hash",
        is_active=True,
    )

    db.add_all([user1, user2])
    db.commit()
    db.refresh(user1)
    db.refresh(user2)

    return {
        "user1": user1,
        "user2": user2,
    }
