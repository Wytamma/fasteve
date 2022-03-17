from fasteve import Fasteve, MongoModel, Resource, MongoObjectId, SubResource
from fasteve.utils import Unique, DataRelation
from typing import Optional, List, NewType, Union, Any
from pydantic import EmailStr, SecretStr, Field, MongoModel
from datetime import datetime
from time import sleep


class Data(MongoModel):
    date: datetime  # datetime.date not supported by mongo
    confirmed: int
    deaths: int
    recovered: int
    country_id: MongoObjectId


data = Resource(
    model=Data, resource_methods=["GET", "POST", "DELETE"], item_name="datum"
)


class Leader(MongoModel):
    name: str
    age: int


leader = Resource(model=Leader, resource_methods=["GET", "POST", "DELETE"])


class Countries(MongoModel):
    name: Unique(str)
    # leader: DataRelation = leader


data_sub_resource = SubResource(resource=data, id_field="country_id", name="data")

countries = Resource(
    model=Countries,
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
