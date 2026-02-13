from app.models import DBRequestSubtype, DBRequestType, DbUser


def seed_types_and_subtypes(db):
    hardware = DBRequestType(name="Hardware")
    software = DBRequestType(name="Software")

    db.add_all([hardware, software])
    db.flush()

    laptop = DBRequestSubtype(name="Laptop", type_id=hardware.id)
    desktop = DBRequestSubtype(name="Desktop", type_id=hardware.id)
    license = DBRequestSubtype(name="License", type_id=software.id)

    db.add_all([laptop, desktop, license])
    db.commit()

    return {
        "hardware": hardware,
        "software": software,
        "laptop": laptop,
        "desktop": desktop,
        "license": license,
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
