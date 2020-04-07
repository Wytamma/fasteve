from dataclasses import dataclass, field
from typing import List, Type, Optional
from pydantic import BaseModel


@dataclass
class Resource:
    schema: Type[BaseModel]
    name: Optional[str] = None  # type: ignore # set name to lowercase schema name by default
    item_name: Optional[str] = None  # type: ignore # set to name by default
    resource_methods: List[str] = field(default_factory=lambda: ["GET"])
    item_methods: List[str] = field(default_factory=lambda: ["GET"])
    in_schema: Optional[Type[BaseModel]] = None  # type: ignore # schema used as default
    response_model: Optional[Type[BaseModel]] = None  # type: ignore # schema used as default
    response_model_include: set = field(default_factory=lambda: set()) # TODO
    response_model_exclude: set = field(default_factory=lambda: set()) # TODO
    alt_id: Optional[str] = None

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
        if not self.in_schema:
            self.in_schema = self.schema
        if not self.response_model:
            self.response_model = self.schema
