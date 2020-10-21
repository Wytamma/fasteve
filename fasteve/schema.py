from pydantic import BaseModel, Field
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


class ItemLinksModel(BaseModel):
    self: Optional[LinkModel]
    parent: Optional[LinkModel]


class BaseResponseSchema(BaseSchema):
    meta: Optional[MetaModel] = Field(
        "MetaModel",
        alias="_meta",
    )
    links: Optional[LinksModel] = Field("LinksModel", alias="_links")


class ItemBaseResponseSchema(BaseSchema):
    links: Optional[ItemLinksModel] = Field("ItemLinksModel", alias="_links")
