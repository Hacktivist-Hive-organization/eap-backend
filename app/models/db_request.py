# app/models/db_request.py
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.common.enums import Priority, Status
from app.database.base import Base


class DBRequest(Base):
    __tablename__ = "requests"

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey("request_types.id"), nullable=False)
    subtype_id = Column(Integer, ForeignKey("request_subtypes.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=False)
    business_justification = Column(String(1000), nullable=False)
    priority = Column(Enum(Priority), nullable=False)
    status = Column(Enum(Status), nullable=False, default=Status.DRAFT)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    #  relationships
    type = relationship("DBRequestType")
    subtype = relationship("DBRequestSubtype")
    requester = relationship(
        "DbUser", foreign_keys=[requester_id], back_populates="user_reqs"
    )
