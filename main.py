from fasteve import Fasteve, BaseSchema, Resource, ObjectID
from fasteve.utils import repeat_every
from typing import Optional
from pydantic import EmailStr, SecretStr, Field
from datetime import date

class People(BaseSchema):
    name: str

people = Resource(schema=People, resource_methods=['GET', 'POST'], item_name='person')

class Ducks(BaseSchema):
    name: str
    age: int
    fav_food: str
    owner_id: Optional[ObjectID]

ducks = Resource(schema=Ducks, resource_methods=['GET', 'POST', 'DELETE'])


"""
GET /countries/{thailand:_id}
[
    {
      "date": "2020-1-22",
      "confirmed": 2,
      "deaths": 0,
      "recovered": 0
    },
    {
      "date": "2020-1-23",
      "confirmed": 3,
      "deaths": 0,
      "recovered": 0
    },
    ...
  ],
"""
class Countries(BaseSchema):
    date: date
    confirmed: int
    deaths: int
    recovered: int

countries = Resource(schema=Countries, resource_methods=['GET', 'POST', 'DELETE'], item_name='country')

resources = [people, ducks, countries]

app = Fasteve(resources=resources, cors_origins=["*"])

@app.on_event("startup")
@repeat_every(seconds=5)
def load_data_from_github() -> None:
    print('Loading data from github --> Fasteve')