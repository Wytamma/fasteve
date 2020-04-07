from fasteve import Fasteve, BaseSchema, Resource, ObjectID
from fasteve.utils import repeat_every, Unique
from typing import Optional, List, NewType
from pydantic import EmailStr, SecretStr, Field, BaseModel
from datetime import datetime

class CovidData(BaseModel):
  date: datetime # datetime.date not supported by mongo
  confirmed: int
  deaths: int
  recovered: int

class Countries(BaseSchema):
  name: Unique(str)
  data: List[CovidData]

countries = Resource(schema=Countries, resource_methods=['GET', 'POST', 'DELETE'], item_name='country', alt_id='name')

resources = [countries]

app = Fasteve(resources=resources, cors_origins=["*"])

@app.on_event("startup")
@repeat_every(seconds=5)
def load_data_from_github() -> None:
  pass
  #print('Loading data from github --> Fasteve')