from fasteve import Fasteve, BaseSchema, Resource

class People(BaseSchema):
    name: str

people = Resource(route="people", schema=People, resource_methods=['GET'])
resources = [people]

app = Fasteve(resources=resources)