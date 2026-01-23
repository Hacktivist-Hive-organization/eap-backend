# app/api/schemas/request_subtype_schema.py

from pydantic import BaseModel

class RequestSubtypeResponseSchema(BaseModel):
    id: int
    name: str
    type_id: int

    class Config:
        from_attributes = True