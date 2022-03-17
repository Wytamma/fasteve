from typing import Optional
from fasteve import Fasteve, Resource, SQLModel, SQLField as Field
from fasteve.io.sql import SQLDataLayer


class HeroBase(SQLModel):
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)


class Hero(HeroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class HeroCreate(HeroBase):
    pass


class HeroRead(HeroBase):
    id: int


class HeroUpdate(SQLModel):
    name: Optional[str] = None
    secret_name: Optional[str] = None
    age: Optional[int] = None


hero = Resource(
    model=Hero,
    response_model=HeroRead,
    create_model=HeroCreate,
    update_model=HeroUpdate,
    resource_methods=["GET", "POST"],
    item_methods=["GET", "DELETE", "PATCH"],
)

resources = [hero]

app = Fasteve(resources=resources, data=SQLDataLayer)