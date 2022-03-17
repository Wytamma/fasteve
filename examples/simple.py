from fasteve import Fasteve, MongoModel, Resource, MongoObjectId, MongoField as Field
from typing import Optional


class People(MongoModel):
    #id: Optional[MongoObjectId] = Field(alias="_id")
    name: Optional[str]


people = Resource(
    name="people",
    model=People,
    resource_methods=["GET", "POST", "DELETE"],
    item_methods=["GET", "DELETE", "PUT", "PATCH"],
)

resources = [people]

app = Fasteve(resources=resources)
