from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Union
from fasteve.model import SQLModel, MongoModel


@dataclass
class Resource:
    model: Union[MongoModel, SQLModel]  # in the db
    name: str = ""
    item_name: str = ""
    resource_methods: List[str] = field(default_factory=lambda: ["GET"])
    item_methods: List[str] = field(default_factory=lambda: ["GET"])
    response_model: Union[MongoModel, SQLModel] = None  # type: ignore # model used as default
    create_model: Union[MongoModel, SQLModel] = None  # type: ignore # model used as default
    update_model: Union[MongoModel, SQLModel] = None  # type: ignore # create_model used as default
    alt_id: Optional[str] = None
    sub_resources: List[SubResource] = field(default_factory=lambda: list())

    allowed_filters: bool = True
    projection: bool = True
    sorting: bool = True
    embedding: bool = True
    datasource: Optional[dict] = None
    bulk_create: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.model.__name__.lower()  # type: ignore

        if not self.item_name:
            if self.name.endswith("s"):
                self.item_name = self.name[:-1]
            else:
                self.item_name = self.name

        if not self.response_model:
            self.response_model = self.model

        if not self.create_model:
            self.create_model = self.model

        if not self.update_model:
            self.update_model = self.create_model


@dataclass
class SubResource:
    # sub resource should set the id on the parent automajically
    resource: Resource
    id_field: str
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.resource.model.name  # type: ignore # set name to resource model name by default
