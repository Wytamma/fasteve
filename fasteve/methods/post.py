from starlette.requests import Request
from datetime import datetime


def set_times(item, now):
    item["_created"] = now
    item["_updated"] = now


async def post(request: Request) -> dict:

    payload = request.payload
    now = datetime.now()

    if type(payload) == list:
        for item in payload:
            item["_created"] = now
            item["_updated"] = now
        try:
            # TODO: bulk insert
            documents = await request.app.data.insert_many(
                request.state.resource, payload
            )
        except Exception as e:
            raise e
    else:
        payload["_created"] = now
        payload["_updated"] = now
        try:
            documents = await request.app.data.insert(request.state.resource, payload)
        except Exception as e:
            raise e

    response = {}

    response["data"] = documents

    return response


def getitem() -> dict:
    return {}
