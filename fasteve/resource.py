from dataclasses import dataclass
from typing import List, Type
from pydantic import BaseModel


@dataclass
class Resource:
    route: str
    schema: Type[BaseModel]
    resource_methods: List[str]
    in_schema: Type[BaseModel] = None
