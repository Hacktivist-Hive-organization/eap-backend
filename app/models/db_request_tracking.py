# app/models/db_request.py
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.common.enums import Priority, Status
from app.database.base import Base


class DBRequestTracking(Base):
    __tablename__ = "request_tracking"

    id = Column(Integer, primary_key=True)
    comment = Column(String(2000))
    status = Column(Enum(Status), nullable=False, default=Status.SUBMITTED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    #  relationships
    request = relationship(
        "DBRequest", foreign_keys=[request_id], back_populates="req_tracking"
    )

    user = relationship("DbUser", foreign_keys=[user_id], back_populates="req_tracking")
    approver = relationship("DbUser", foreign_keys=[approver_id])
