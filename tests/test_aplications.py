from fasteve import Fasteve, BaseSchema, Resource
from starlette.testclient import TestClient
import pytest
from pytest import fixture
from fasteve.io.mongo import MongoClient

class People(BaseSchema):
    name: str

people = Resource(name="people", schema=People, resource_methods=["GET", "POST"])

resources = [people]

app = Fasteve(resources=resources)

@fixture(scope="session")
def test_user():
    return {
        "user": {
            "email": "user1@example.com",
            "password": "string1",
            "username": "string1"
        }
    }


@fixture(scope="session")
def test_client(test_user):
    app.config.MONGODB_DATABASE = 'testing'
    with TestClient(app) as test_client:
        yield test_client

    import asyncio
    db = asyncio.run(MongoClient.get_database())
    db.drop_database(app.config.MONGODB_DATABASE)


@pytest.mark.parametrize(
    "path,expected_status,expected_response",
    [
        ("/", 200, {"links": {"child": [{"href": "/people", "title": "people"}]}}),
        (
            "/people",
            200,
            {
                "data": [],
                "meta": {"max_results": 25, "total": 0, "page": 1},
                "links": {
                    "self": {"href": "/people", "title": "people"},
                    "parent": {"href": "/", "title": "home"},
                },
            },
        ),
        ("/nonexistent", 404, {"detail": "Not Found"}),
    ],
)
def test_get_path(test_client, path, expected_status, expected_response):
    response = test_client.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "path,data,expected_status,expected_response",
    [
        (
            "/people",
            {
                "name": "Curie"
            },
            200,
            {
                "name": "Curie"
            }
        ),
    ],
)
def test_post_path(test_client, path, data, expected_status, expected_response):
    response = test_client.post(path, json={'name': 'Curie'})
    assert response.status_code == expected_status
    # what's the correct response?
    assert response.json()['data'][0]['name'] == expected_response['name']
