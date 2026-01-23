# app/models/db_request_subtype.py
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.session import Base

class DBRequestSubtype(Base):
    __tablename__ = "request_subtypes"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type_id = Column(Integer, ForeignKey("request_types.id"), nullable=False)

    type = relationship("DBRequestType", back_populates="subtypes")
