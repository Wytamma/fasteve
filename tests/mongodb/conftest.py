import pytest
from starlette.config import environ
import docker

PORT = 27017
environ["FASTEVE_MONGODB_URI"] = f"mongodb://localhost:{PORT}"
environ["FASTEVE_MONGODB_NAME"] = "fasteve_testing"


@pytest.fixture(scope="session", autouse=True)
def drop_database():
    # Start mongodb docker
    client = docker.from_env()
    container = client.containers.run(
        "mongo", detach=True, auto_remove=True, ports={"27017": 27017}
    )
    yield
    # Stop mongodb after testing finished
    container.kill()
