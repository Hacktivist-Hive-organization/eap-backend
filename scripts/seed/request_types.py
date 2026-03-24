from sqlalchemy.orm import Session

from app.models.db_request_subtype import DBRequestSubtype
from app.models.db_request_type import DBRequestType
from app.models.db_request_type_approver import DBRequestTypeApprover
from app.models.db_user import DbUser


def seed_request_type_subtype_data(db: Session):
    if db.query(DBRequestType).count() > 0:
        return

    # Create types
    hardware = DBRequestType(name="Hardware")
    software = DBRequestType(name="Software & Access")
    services = DBRequestType(name="Services & Facilities")

    db.add_all([hardware, software, services])
    db.flush()  # flush to get IDs

    # Create subtypes
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
    db.flush()

    # Assign 2 approvers per type with different workloads
    approvers = db.query(DbUser).filter(DbUser.role == "APPROVER").all()
    type_list = [hardware, software, services]

    for i, rt in enumerate(type_list):
        a1 = approvers[i * 2]
        a2 = approvers[i * 2 + 1]
        db.add_all(
            [
                DBRequestTypeApprover(
                    request_type_id=rt.id, user_id=a1.id, workload=i + 1
                ),
                DBRequestTypeApprover(
                    request_type_id=rt.id, user_id=a2.id, workload=(i + 1) * 2
                ),
            ]
        )
    db.commit()
