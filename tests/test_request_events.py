from fasteve import Fasteve, BaseSchema, Resource
from starlette.requests import Request
from starlette.testclient import TestClient


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


# life cycle
@app.on_event("startup")
async def startup_event():
    events.append("startup")


@app.on_event("shutdown")
async def shutdown_event():
    events.append("shutdown")


# method
@app.on_event("before_GET")
async def before_GET_callback(request: Request, name):
    events.append("before_GET")


@app.on_event("before_POST")
async def before_POST_callback(request: Request, name):
    events.append("before_POST")


@app.on_event("before_DELETE")
async def before_DELETE_callback(request: Request, name):
    events.append("before_DELETE")


@app.on_event("after_GET")
async def after_GET_callback(request: Request, response, name):
    events.append("after_GET")


@app.on_event("after_POST")
async def after_POST_callback(request: Request, response, name):
    events.append("after_POST")


@app.on_event("after_DELETE")
async def after_DELETE_callback(request: Request, response, name):
    events.append("after_DELETE")


# resource
@app.on_event("before_GET_people")
async def before_GET_people_callback(request: Request):
    events.append("before_GET_people")


@app.on_event("before_POST_people")
async def before_POST_people_callback(request: Request):
    events.append("before_POST_people")


@app.on_event("before_DELETE_people")
async def before_DELETE_people_callback(request: Request):
    events.append("before_DELETE_people")


@app.on_event("after_GET_people")
async def after_GET_people_callback(request: Request, response):
    events.append("after_GET_people")


@app.on_event("after_POST_people")
async def after_POST_people_callback(request: Request, response):
    events.append("after_POST_people")


@app.on_event("after_DELETE_people")
async def after_DELETE_people_callback(request: Request, response):
    events.append("after_DELETE_people")


events = []


def test_startup():
    with TestClient(app) as test_client:
        assert "startup" in events


def test_shutdown():
    with TestClient(app) as test_client:
        assert "shutdown" in events


def test_request_events():
    with TestClient(app) as test_client:
        response = test_client.get("/people")
        data = {"name": "Curie"}
        response = test_client.post("/people", json=data)
        test_client.delete("/people")

        assert "before_GET_people" in events
        assert "before_POST_people" in events
        assert "before_DELETE_people" in events

        assert "before_GET" in events
        assert "before_POST" in events
        assert "before_DELETE" in events

        assert "after_GET_people" in events
        assert "after_POST_people" in events
        assert "after_DELETE_people" in events

        assert "after_GET" in events
        assert "after_POST" in events
        assert "after_DELETE" in events
