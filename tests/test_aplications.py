from fasteve import Fasteve, BaseSchema, Resource
from starlette.testclient import TestClient
import pytest


class People(BaseSchema):
    name: str

people = Resource(route="people", schema=People, resource_methods=["GET", "POST"])

resources = [people]

app = Fasteve(resources=resources)

client = TestClient(app)


@pytest.mark.parametrize(
    "path,expected_status,expected_response",
    [
        ("/", 200, {"_links": {"child": [{"href": "/people", "title": "people"}]}}),
        (
            "/people",
            200,
            {
                "_items": [],
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
    response = client.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.parametrize(
    "path,expected_status,expected_response,data",
    [
        ("/", 405, {"detail": "Method Not Allowed"}, {}),
        (
            "/people",
            200,
            {
            },
            {}
        ),
    ],
)
def test_post_path(path, expected_status, expected_response, data):
    response = client.post(path, data)
    assert response.status_code == expected_status
    assert response.json() == expected_response
