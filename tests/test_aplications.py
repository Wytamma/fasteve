from fasteve import Fasteve, BaseSchema
from starlette.testclient import TestClient
import pytest


class People(BaseSchema):
    name: str


settings = {"DOMAIN": {"people": {"schema": People}}}

app = Fasteve(settings=settings)

client = TestClient(app)


@pytest.mark.parametrize(
    "path,expected_status,expected_response",
    [
        ("/", 200, {"_links": {"child": [{"href": "people", "title": "people"}]}}),
        (
            "/people",
            200,
            {
                "_items": [],
                "_meta": {"max_results": 25, "total": 0, "page": 1},
                "_links": {
                    "self": {"href": "people", "title": "people"},
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
