# app/models/db_request_type.py
from sqlalchemy import Column, Integer, String
from app.database.session import Base

class DBRequestType(Base):
    __tablename__ = "request_types"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
