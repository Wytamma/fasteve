from fasteve import Fasteve, BaseSchema, Resource, ObjectID
from typing import Optional
from pydantic import EmailStr, SecretStr, Field

class People(BaseSchema):
    name: str

people = Resource(schema=People, resource_methods=['GET', 'POST'], item_name='person')

class Ducks(BaseSchema):
    name: str
    age: int
    fav_food: str
    owner_id: Optional[ObjectID]

ducks = Resource(schema=Ducks, resource_methods=['GET', 'POST'])

class AccountsOut(BaseSchema):
    name: str
    email: EmailStr

class AccountsIn(AccountsOut):
    password: str = Field(
        ...,
        min_length=8
    )

accounts = Resource(
    name='accounts',
    schema=AccountsIn, 
    resource_methods=['GET', 'POST'], 
    response_model=AccountsOut,
    bulk_inserts = False
    )

resources = [people, ducks, accounts]

app = Fasteve(resources=resources)