from pydantic import BaseModel as PydanticBaseModel, Field
from sqlmodel import SQLModel as SQLModelBase
from typing import Optional
from bson import ObjectId

json_encoders = {ObjectId: lambda x: str(x)}


class SQLModel(SQLModelBase):
    @classmethod
    def get_primary_key(cls) -> str:
        for field in cls.__fields__:
            if hasattr(cls.__fields__[field].field_info, "primary_key"):
                if cls.__fields__[field].field_info.primary_key:  # type: ignore
                    return field
        raise ValueError(f"Could not find primary_key in {cls}")

    class Config:
        json_encoders = json_encoders


class BaseModel(PydanticBaseModel):
    class Config:
        json_encoders = json_encoders


class MongoModel(BaseModel):
    @classmethod
    def get_primary_key(self) -> str:
        return "_id"


class MetaModel(PydanticBaseModel):
    page: Optional[int]
    max_results: Optional[int]
    total: Optional[int]


class LinkModel(PydanticBaseModel):
    href: str
    title: str


class LinksModel(PydanticBaseModel):
    self: Optional[LinkModel]
    parent: Optional[LinkModel]
    next: Optional[LinkModel]
    last: Optional[LinkModel]


class ItemLinksModel(PydanticBaseModel):
    self: Optional[LinkModel]
    parent: Optional[LinkModel]


class BaseResponseModel(BaseModel):
    meta: Optional[MetaModel] = Field(
        "MetaModel",
        alias="_meta",
    )
    links: Optional[LinksModel] = Field("LinksModel", alias="_links")


class ItemBaseResponseModel(BaseModel):
    links: Optional[ItemLinksModel] = Field("ItemLinksModel", alias="_links")
