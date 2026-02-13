#  app/api/schemas/request_type_schema.py

from typing import List

from pydantic import BaseModel


class RequestSubtypeResponseSchema(BaseModel):
    id: int
    name: str

    class ConfigDict:
        from_attributes = True


class RequestTypeResponseSchema(BaseModel):
    id: int
    name: str
    subtypes: List[RequestSubtypeResponseSchema]

    class ConfigDict:
        from_attributes = True
