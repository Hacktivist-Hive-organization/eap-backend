#pp/database/seed_request_data.py
from app.models.db_request_subtype import DBRequestSubtype
from app.models.db_request_type import DBRequestType


def seed_request_data(db):
    if db.query(DBRequestType).count() > 0:
        return  # already seeded

    hardware = DBRequestType(name="Hardware")
    software = DBRequestType(name="Software & Access")
    services = DBRequestType(name="Services & Facilities")

    db.add_all([hardware, software, services])
    db.commit()

    db.add_all(
        [
            DBRequestSubtype(name="Laptop", type_id=hardware.id),
            DBRequestSubtype(name="Desktop", type_id=hardware.id),
            DBRequestSubtype(name="Monitor", type_id=hardware.id),
            DBRequestSubtype(name="Peripherals", type_id=hardware.id),
            DBRequestSubtype(name="Mobile device", type_id=hardware.id),
            DBRequestSubtype(name="Other", type_id=hardware.id),
            DBRequestSubtype(name="Software license", type_id=software.id),
            DBRequestSubtype(name="System access", type_id=software.id),
            DBRequestSubtype(name="Application access", type_id=software.id),
            DBRequestSubtype(name="VPN access", type_id=software.id),
            DBRequestSubtype(name="Other", type_id=software.id),
            DBRequestSubtype(name="Parking spot", type_id=services.id),
            DBRequestSubtype(name="Office equipment", type_id=services.id),
            DBRequestSubtype(name="Training/course enrollment", type_id=services.id),
            DBRequestSubtype(name="Travel approval", type_id=services.id),
            DBRequestSubtype(name="Other", type_id=services.id),
        ]
    )

    db.commit()
