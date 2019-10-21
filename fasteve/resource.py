from dataclasses import dataclass
from typing import List, Type
from pydantic import BaseModel


@dataclass
class Resource:
    schema: Type[BaseModel]
    name: str = None  # set name to lowercase schema name by d
    resource_methods: List[str] = None 
    in_schema: Type[BaseModel] = None  # schema used as default
    response_model: Type[BaseModel] = None  # schema used as default
    allowed_filters: bool = True
    projection: bool = True
    sorting: bool = True
    embedding: bool = True
    datasource: dict = None

    def __post_init__(self):
        if not self.name:
            self.name = self.schema.__name__.lower()
        if not self.in_schema:
            self.in_schema = self.schema
        if not self.response_model:
            self.response_model = self.schema
        if not self.resource_methods:
            # TODO: set with config?
            self.resource_methods = ['GET', 'HEAD']