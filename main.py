from fasteve import Fasteve, BaseSchema, Resource

class People(BaseSchema):
    name: str

people = Resource(name="people", schema=People, resource_methods=['GET', 'POST'])
resources = [people]

app = Fasteve(resources=resources)