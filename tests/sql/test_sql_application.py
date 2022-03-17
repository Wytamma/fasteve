from typing import Optional
from starlette.testclient import TestClient
import pytest

from fasteve import Fasteve, Resource, SQLModel, SQLDataLayer
from sqlmodel import Field


class People(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str = Field()


people = Resource(
    model=People,
    resource_methods=["GET", "POST", "DELETE"],
    item_methods=["GET", "DELETE", "PUT", "PATCH"],
)

resources = [people]

app = Fasteve(resources=resources, data=SQLDataLayer)


@pytest.fixture()
def test_client():

    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize(
    "path,expected_status,expected_response",
    [
        ("/", 200, {"_links": {"child": [{"href": "/people", "title": "people"}]}}),
        (
            "/people",
            200,
            {
                "_data": [],
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
def test_get_path(test_client, path, expected_status, expected_response):
    response = test_client.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "path,data,expected_status,expected_response",
    [
        ("/people", {"name": "Curie"}, 201, {"name": "Curie"}),
    ],
)
def test_insert(test_client, path, data, expected_status, expected_response):
    response = test_client.post(path, json=data)
    assert response.status_code == expected_status
    # what's the correct response?
    assert response.json()["_data"][0]["name"] == expected_response["name"]
    assert "id" in response.json()["_data"][0].keys()


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
def test_bulk_insert(test_client, path, data, expected_status, expected_response):
    response = test_client.post(path, json=data)
    assert response.status_code == expected_status
    result = [{"name": person["name"]} for person in response.json()["_data"]]
    assert data == result


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Curie"}, 200),
    ],
)
def test_get_item(test_client, path, data, expected_status):
    response = test_client.post(path, json=data)  # insert data for test
    response.json()["_data"][0]
    itemid = response.json()["_data"][0]["id"]
    response = test_client.get(path + f"/{itemid}")
    print(response.json())
    assert response.status_code == expected_status
    assert itemid == response.json()["_data"][0]["id"]


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Curie"}, 204),
    ],
)
def test_delete_path(test_client, path, data, expected_status):
    _ = test_client.post(path, json=data)  # insert data for test
    response = test_client.delete(path)
    assert response.status_code == expected_status
    response = test_client.get(path)
    assert len(response.json()["_data"]) == 0


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Curie"}, 204),
    ],
)
def test_delete_item(test_client, path, data, expected_status):
    response = test_client.post(path, json=data)  # insert data for test
    itemid = response.json()["_data"][0]["id"]
    response = test_client.delete(path + f"/{itemid}")
    assert response.status_code == expected_status
    response = test_client.get(path + f"/{itemid}")
    assert response.status_code == 404


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Lovelace"}, 204),
    ],
)
def test_put_replace_item(test_client, path, data, expected_status):
    response = test_client.post(path, json={"name": "Curie"})  # insert data for test
    itemid = response.json()["_data"][0]["id"]
    response = test_client.put(path + f"/{itemid}", json=data)
    assert response.status_code == expected_status
    response = test_client.get(path + f"/{itemid}")
    item = response.json()["_data"][0]
    assert item["name"] == data["name"]
    assert item["id"] == itemid


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Lovelace"}, 204),
    ],
)
def test_put_insert_item(test_client, path, data, expected_status):
    itemid = 42
    response = test_client.put(path + f"/{itemid}", json=data)
    assert response.status_code == expected_status
    response = test_client.get(path + f"/{itemid}")
    assert response.status_code == 200
    item = response.json()["_data"][0]
    assert item["name"] == data["name"]
    assert item["id"] == itemid


@pytest.mark.parametrize(
    "path,data,expected_status",
    [
        ("/people", {"name": "Lovelace"}, 204),
    ],
)
def test_patch_item(test_client, path, data, expected_status):
    response = test_client.post(path, json={"name": "Curie"})  # insert data for test
    itemid = response.json()["_data"][0]["id"]
    response = test_client.patch(path + f"/{itemid}", json=data)
    assert response.status_code == expected_status
    response = test_client.get(path + f"/{itemid}")
    item = response.json()["_data"][0]
    assert item["name"] == data["name"]
    assert item["id"] == itemid
