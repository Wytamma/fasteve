from pydantic import BaseModel
from typing import Optional
from bson import ObjectId

json_encoders = {ObjectId: lambda x: str(x)}


class BaseSchema(BaseModel):
    class Config:
        json_encoders = json_encoders


class MetaModel(BaseModel):
    page: Optional[int]
    max_results: Optional[int]
    total: Optional[int]


class LinkModel(BaseModel):
    href: str
    title: str


class LinksModel(BaseModel):
    self: Optional[LinkModel]
    parent: Optional[LinkModel]
    next: Optional[LinkModel]
    last: Optional[LinkModel]


class BaseResponseSchema(BaseSchema):
    meta: Optional[MetaModel]
    links: Optional[LinksModel]
