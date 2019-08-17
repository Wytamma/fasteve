from pydantic import BaseModel
from uuid import UUID


class BaseSchema(BaseModel):
    _id: UUID = None 
