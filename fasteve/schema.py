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
    pass

class BaseOutSchema(BaseSchema):
    id:  ObjectIdStr
    updated: datetime
    created: datetime

class MetaModel(BaseSchema):
    page: Optional[int]
    max_results: Optional[int]
    total: Optional[int]

class BaseResponseSchema(BaseSchema):
    meta: Optional[MetaModel]
    links: Optional[dict]