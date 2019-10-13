from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class BaseSchema(BaseModel):
    _id: UUID

class BaseResponseSchema(BaseModel):
    meta: dict = {}
    links: dict = {}