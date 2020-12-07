from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Type
from pydantic import BaseModel


@dataclass
class Resource:
    schema: Type[BaseModel]  # in the db
    name: str = ""
    item_name: str = ""
    resource_methods: List[str] = field(default_factory=lambda: ["GET"])
    item_methods: List[str] = field(default_factory=lambda: ["GET"])
    response_model: Type[BaseModel] = None  # type: ignore # schema used as default
    response_model_include: set = field(default_factory=lambda: set())  # TODO
    response_model_exclude: set = field(default_factory=lambda: set())  # TODO
    alt_id: Optional[str] = None
    sub_resources: List[SubResource] = field(default_factory=lambda: list())

    allowed_filters: bool = True
    projection: bool = True
    sorting: bool = True
    embedding: bool = True
    datasource: Optional[dict] = None
    bulk_inserts: bool = True

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.schema.__name__.lower()
        if not self.item_name:
            if self.name.endswith("s"):
                self.item_name = self.name[:-1]
            else:
                self.item_name = self.name
        if not self.response_model:
            self.response_model = self.schema


@dataclass
class SubResource:
    # sub resource should set the id on the parent automajically
    resource: Resource
    id_field: str
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.resource.schema.name  # type: ignore # set name to resource schema name by default
