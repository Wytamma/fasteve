from fasteve import Fasteve, BaseSchema, Resource
from typing import Optional


class People(BaseSchema):
    name: str
    age: int


people = Resource(
    name="people",
    schema=People,
    resource_methods=["GET", "POST", "DELETE"],
    item_methods=["GET", "DELETE", "PUT", "PATCH"],
    bulk_inserts=False,
)

resources = [people]

app = Fasteve(resources=resources)
