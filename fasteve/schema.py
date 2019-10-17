from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class BaseSchema(BaseModel):
    id: Optional[str]
    etag: Optional[str]
    updated: Optional[str]
    created: Optional[str]

class BaseResponseSchema(BaseModel):
    meta: dict = {}
    links: dict = {}