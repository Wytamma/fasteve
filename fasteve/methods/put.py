from starlette.requests import Request
from datetime import datetime
from fasteve.methods.post import post
from fasteve.methods.common import get_document
from typing import Union
from fasteve.core.utils import ObjectID
from fastapi import Response


async def put_item(request: Request, item_id: Union[ObjectID, str]) -> Response:
    orginal_document = await get_document(request, item_id)
    payload = getattr(request, "payload")

    if not orginal_document:
        # insert
        if ObjectID.is_valid(item_id):
            payload["_id"] = item_id
        # if it is not valid must be an alt_id
        setattr(request, "payload", [payload])  # post expects a list
        await post(request)
        return Response(status_code=204)

    # replace
    now = datetime.now()
    payload["_created"] = orginal_document["_created"]
    payload["_updated"] = now

    try:
        document = await request.app.data.replace_item(
            request.state.resource, orginal_document["_id"], payload
        )
    except Exception as e:
        raise e
    return Response(status_code=204)
