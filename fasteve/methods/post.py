from starlette.requests import Request
from datetime import datetime
from ..core import config


async def post(request: Request) -> dict:

    payload = getattr(request, "payload")
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
            document = await request.app.data.insert(request.state.resource, payload)
            documents = [document]
        except Exception as e:
            raise e

    response = {}

    response[config.DATA] = documents

    return response
