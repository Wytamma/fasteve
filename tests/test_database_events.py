from fasteve import Fasteve, BaseSchema, Resource
from starlette.testclient import TestClient
import pytest


class People(BaseSchema):
    name: str


people = Resource(
    name="people",
    schema=People,
    resource_methods=["GET", "POST", "DELETE"],
    item_methods=["GET", "DELETE", "PUT", "PATCH"],
)

resources = [people]

app = Fasteve(resources=resources)

app.config.MONGODB_DATABASE = "testing"


@app.on_event("after_fetch_resource")
async def after_fetch_resource_callback(name, response):
    events.append("after_fetch_resource")


@app.on_event("after_fetch_item")
async def after_fetch_item_callback(name, response):
    events.append("after_fetch_item")


events = []


def test_database_events():
    with TestClient(app) as test_client:
        response = test_client.get("/people")
        data = {"name": "Curie"}
        response = test_client.post("/people", json=data)
        response = test_client.get(f"/people/{response.json()['_data'][0]['_id']}")

    assert "after_fetch_resource" in events
    assert "after_fetch_item" in events
