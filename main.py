from fasteve import Fasteve, BaseSchema, Resource, ObjectID
from fasteve.utils import Unique, DataRelation, SubResource
from typing import Optional, List, NewType
from pydantic import EmailStr, SecretStr, Field, BaseModel
from datetime import datetime

class Data(BaseSchema):
  date: datetime # datetime.date not supported by mongo
  confirmed: int
  deaths: int
  recovered: int
  country_id: ObjectID

data = Resource(schema=Data, resource_methods=['GET', 'POST', 'DELETE'], item_name='datum')

class Leader(BaseSchema):
  name: str
  age: int 

leader = Resource(schema=Leader, resource_methods=['GET', 'POST', 'DELETE'])

class Countries(BaseSchema):
  name: Unique(str)
  leader: DataRelation(resource=leader) # embed Union[ObjectID, leader.schema]

data_sub_resource = SubResource(resource=data, id_field='country_id', name='data')

countries = Resource(
    schema=Countries, 
    resource_methods=['GET', 'POST', 'DELETE'], 
    item_name='country', 
    alt_id='name', 
    sub_resources=[data_sub_resources]
  )

resources = [countries, leader, data]

app = Fasteve(resources=resources, cors_origins=["*"])

@app.repeat_every(seconds=60 * 60 * 24)  # every day
def load_data_from_github() -> None:
  print('Loading data from github --> Fasteve')