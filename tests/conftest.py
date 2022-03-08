import pytest
from fasteve.io.mongo import MongoClient


@pytest.fixture(scope="module", autouse=True)
def drop_database():
    yield
    # Delete database testing after test already finished
    MongoClient.connect()
    db = MongoClient.get_database()
    db.drop_database("testing")
    db.close()


# @pytest.fixture(scope="module")
# def test_client():

#     with TestClient(app) as test_client:
#         yield test_client
