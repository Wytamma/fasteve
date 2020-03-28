from pydantic import BaseModel, BaseConfig
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

json_encoders = {
    ObjectId: lambda x: str(x)
}

class BaseSchema(BaseModel):
    class Config:
        json_encoders = json_encoders

class MetaModel(BaseModel):
    page: Optional[int]
    max_results: Optional[int]
    total: Optional[int]

class BaseResponseSchema(BaseModel):
    meta: Optional[MetaModel]
    links: Optional[dict]