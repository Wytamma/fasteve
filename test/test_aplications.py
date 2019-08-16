from fasteve import Fasteve
from starlette.testclient import TestClient
import pytest

settings = {'DOMAIN': {'people': {}}}

app = Fasteve(settings=settings)

@app.api_route("/api_route")
def non_operation():
    return {"message": "Hello World"}


def non_decorated_route():
    return {"message": "Hello World"}


app.add_api_route("/non_decorated_route", non_decorated_route)

client = TestClient(app)

@pytest.mark.parametrize(
    "path,expected_status,expected_response",
    [
        ("/people", 200, {}),
        ("/api_route", 200, {"message": "Hello World"}),
        ("/non_decorated_route", 200, {"message": "Hello World"}),
        ("/nonexistent", 404, {"detail": "Not Found"}),
    ],
)
def test_get_path(path, expected_status, expected_response):
    response = client.get(path)
    assert response.status_code == expected_status
    assert response.json() == expected_response
