from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId
from bson import ObjectId
from datetime import datetime


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise ValueError("Not a valid ObjectId")
        return str(v)


class BaseSchema(BaseModel):
    id:  Optional[ObjectIdStr]
    etag: Optional[str]
    updated: Optional[datetime]
    created: Optional[datetime]

class BaseResponseSchema(BaseModel):
    meta: dict = {}
    links: dict = {}