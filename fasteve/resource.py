from dataclasses import dataclass, field
from typing import List, Type
from pydantic import BaseModel


@dataclass
class Resource:
    schema: Type[BaseModel]
    name: str = None  # set name to lowercase schema name by default
    item_name: str = None  # set to name by default
    resource_methods: List[str] = field(default_factory=lambda: ["GET"])
    item_methods: List[str] = field(default_factory=lambda: ["GET"])
    in_schema: Type[BaseModel] = None  # schema used as default
    response_model: Type[BaseModel] = None  # schema used as default
    allowed_filters: bool = True
    projection: bool = True
    sorting: bool = True
    embedding: bool = True
    datasource: dict = None
    bulk_inserts: bool = True

    def __post_init__(self):
        if not self.name:
            self.name = self.schema.__name__.lower()
        if not self.item_name:
            if self.name.endswith("s"):
                self.item_name = self.name[:-1]
            else:
                self.item_name = self.name
        if not self.in_schema:
            self.in_schema = self.schema
        if not self.response_model:
            self.response_model = self.schema
        if not self.resource_methods:
            # TODO: set with config?
            self.resource_methods = ["GET", "HEAD"]
