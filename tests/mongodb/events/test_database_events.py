from typing import Optional
from fasteve import Fasteve, MongoModel, Resource, MongoObjectId
from starlette.testclient import TestClient
from pydantic import Field


class People(MongoModel):
    id: Optional[MongoObjectId] = Field(alias="_id")
    name: Optional[str]


people = Resource(
    name="people",
    model=People,
    resource_methods=["GET", "POST", "DELETE"],
    item_methods=["GET", "DELETE", "PUT", "PATCH"],
)

resources = [people]

app = Fasteve(resources=resources)


@app.on_event("after_read_resource")
async def after_read_resource_callback(name, response):
    events.append("after_read_resource")


@app.on_event("after_read_item")
async def after_read_item_callback(name, response):
    events.append("after_read_item")


events = []


def test_database_events():
    with TestClient(app) as test_client:
        response = test_client.get("/people")
        data = {"name": "Curie"}
        response = test_client.post("/people", json=data)
        response = test_client.get(f"/people/{response.json()['_data'][0]['_id']}")

    assert "after_read_resource" in events
    assert "after_read_item" in events
