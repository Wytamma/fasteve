from fasteve import Fasteve, BaseSchema, Resource, ObjectID
from fasteve.utils import Unique, DataRelation, SubResource
from typing import Optional, List, NewType, Union, Any
from pydantic import EmailStr, SecretStr, Field, BaseModel
from datetime import datetime
from time import sleep


class Data(BaseSchema):
    date: datetime  # datetime.date not supported by mongo
    confirmed: int
    deaths: int
    recovered: int
    country_id: ObjectID


data = Resource(
    schema=Data, resource_methods=["GET", "POST", "DELETE"], item_name="datum"
)


class Leader(BaseSchema):
    name: str
    age: int


leader = Resource(schema=Leader, resource_methods=["GET", "POST", "DELETE"])


class Countries(BaseSchema):
    name: Unique(str)
    leader: ObjectID = DataRelation(leader)


data_sub_resource = SubResource(resource=data, id_field="country_id", name="data")

countries = Resource(
    schema=Countries,
    resource_methods=["GET", "POST", "DELETE"],
    item_name="country",
    alt_id="name",
    sub_resources=[data_sub_resource],  # GET /countries/<country_id|name>/data
)

resources = [countries, leader, data]

app = Fasteve(resources=resources, cors_origins=["*"])


@app.repeat_every(seconds=60 * 60 * 24)  # every day
async def count_countries_in_db() -> None:
    data, count = await app.data.find(countries)
    print(f"There are {count} countries in the database!")


@app.get("/custom_endpoint")
def custom_endpoint():
    return {"custom": "endpoint"}
