from app.models import DBRequestType, DBRequestSubtype, DbUser


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
    user1 = DbUser(username= "user1")

    db.add_all([user1])
    db.commit()

    return {
        "user1": user1,
    }
