from starlette.requests import Request
from datetime import datetime
from ..core import config


async def post(request: Request) -> dict:

    payload = getattr(request, "payload")

    now = datetime.now()

    for item in payload:
        item["_created"] = now
        item["_updated"] = now

    if len(payload) > 1:
        try:
            # TODO: bulk insert
            documents = await request.app.data.insert_many(
                request.state.resource, payload
            )
        except Exception as e:
            raise e
    else:
        try:
            payload = payload[0]
            document = await request.app.data.insert(request.state.resource, payload)
            documents = [document]
        except Exception as e:
            raise e

    response = {}

    response[config.DATA] = documents

    return response
