from fasteve import Fasteve, BaseSchema, Resource
from starlette.testclient import TestClient
import pytest
from fasteve.io.mongo import MongoClient
from bson import ObjectId


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


test_client = TestClient(app)


@pytest.fixture(autouse=True, scope="session")
def drop_test_database():
    yield
    import asyncio

    db = asyncio.run(MongoClient.get_database())
    db.drop_database(app.config.MONGODB_DATABASE)
    db.close()


@pytest.mark.parametrize(
    "path,expected_status,expected_response",
    [
        ("/", 200, {"_links": {"child": [{"href": "/people", "title": "people"}]}}),
        (
            "/people",
            200,
            {
                app.config.DATA: [],
                "_meta": {"max_results": 25, "total": 0, "page": 1},
                "_links": {
                    "self": {"href": "/people", "title": "people"},
                    "parent": {"href": "/", "title": "home"},
                },
            },
        ),
        ("/nonexistent", 404, {"detail": "Not Found"}),
    ],
)
def test_get_path(path, expected_status, expected_response):
    response = test_client.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "path,data,expected_status,expected_response",
    [
        ("/people", {"name": "Curie"}, 201, {"name": "Curie"}),
    ],
)
def test_insert(path, data, expected_status, expected_response):
    response = test_client.post(path, json=data)
    assert response.status_code == expected_status
    # what's the correct response?
    assert response.json()[app.config.DATA][0]["name"] == expected_response["name"]
    assert "_id" in response.json()[app.config.DATA][0].keys()


@pytest.mark.parametrize(
    "path,data,expected_status,expected_response",
    [
        (
            "/people",
            [
                {"name": "Marie Curie"},
                {"name": "Rosalind Franklin"},
                {"name": "Ada Lovelace"},
            ],
            201,
            [
                {"name": "Marie Curie"},
                {"name": "Rosalind Franklin"},
                {"name": "Ada Lovelace"},
            ],
        ),
    ],
)
def test_bulk_insert(path, data, expected_status, expected_response):
    response = test_client.post(path, json=data)
    assert response.status_code == expected_status
    result = [{"name": person["name"]} for person in response.json()[app.config.DATA]]
    assert data == result


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Curie"}, 200),
    ],
)
def test_get_item(path, data, expected_status):
    response = test_client.post(path, json=data)  # insert data for test
    response.json()[app.config.DATA][0]
    item_id = response.json()[app.config.DATA][0]["_id"]
    response = test_client.get(path + f"/{item_id}")
    assert response.status_code == expected_status
    assert item_id == response.json()[app.config.DATA][0]["_id"]


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Curie"}, 204),
    ],
)
def test_delete_path(path, data, expected_status):
    _ = test_client.post(path, json=data)  # insert data for test
    response = test_client.delete(path)
    assert response.status_code == expected_status
    response = test_client.get(path)
    assert len(response.json()[app.config.DATA]) == 0


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Curie"}, 204),
    ],
)
def test_delete_item(path, data, expected_status):
    response = test_client.post(path, json=data)  # insert data for test
    item_id = response.json()[app.config.DATA][0]["_id"]
    response = test_client.delete(path + f"/{item_id}")
    assert response.status_code == expected_status
    response = test_client.get(path + f"/{item_id}")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Lovelace"}, 204),
    ],
)
def test_put_replace_item(path, data, expected_status):
    response = test_client.post(path, json={"name": "Curie"})  # insert data for test
    item_id = response.json()[app.config.DATA][0]["_id"]
    response = test_client.put(path + f"/{item_id}", json=data)
    assert response.status_code == expected_status
    response = test_client.get(path + f"/{item_id}")
    item = response.json()[app.config.DATA][0]
    assert item["name"] == data["name"]
    assert item["_id"] == item_id


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Lovelace"}, 204),
    ],
)
def test_put_insert_item(path, data, expected_status):
    item_id = str(ObjectId())
    response = test_client.put(path + f"/{item_id}", json=data)
    assert response.status_code == expected_status
    response = test_client.get(path + f"/{item_id}")
    assert response.status_code == 200
    item = response.json()[app.config.DATA][0]
    assert item["name"] == data["name"]
    assert item["_id"] == item_id


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Lovelace"}, 204),
    ],
)
def test_patch_item(path, data, expected_status):
    response = test_client.post(path, json={"name": "Curie"})  # insert data for test
    item_id = response.json()[app.config.DATA][0]["_id"]
    response = test_client.patch(path + f"/{item_id}", json=data)
    assert response.status_code == expected_status
    response = test_client.get(path + f"/{item_id}")
    item = response.json()[app.config.DATA][0]
    assert item["name"] == data["name"]
    assert item["_id"] == item_id
