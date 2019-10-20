from dataclasses import dataclass
from typing import List, Type
from pydantic import BaseModel


@dataclass
class Resource:
    name: str
    schema: Type[BaseModel]
    resource_methods: List[str]
    in_schema: Type[BaseModel] = None  # schema used as defualt
    response_model: Type[BaseModel] = None # schema used as defualt
    allowed_filters: bool = True
    projection: bool = True
    sorting: bool = True
    embedding: bool = True
    datasource: dict = None