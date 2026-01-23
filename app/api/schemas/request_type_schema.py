#  app/api/schemas/request_type_schema.py
from pydantic import BaseModel


class RequestTypeResponseSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


