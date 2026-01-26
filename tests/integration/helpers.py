from app.models import DBRequestType, DBRequestSubtype

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
