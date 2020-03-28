from fasteve import Fasteve, BaseSchema, Resource, ObjectID

class People(BaseSchema):
    name: str

people = Resource(schema=People, resource_methods=['GET', 'POST'])

class Ducks(BaseSchema):
    name: str
    age: int
    fav_food: str
    owner_id: ObjectID

ducks = Resource(schema=Ducks, resource_methods=['GET', 'POST'])

resources = [people, ducks]

app = Fasteve(resources=resources)