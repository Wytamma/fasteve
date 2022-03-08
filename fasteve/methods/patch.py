from starlette.requests import Request
from datetime import datetime
from fasteve.methods.common import get_document
from typing import Union
from fasteve.core.utils import ObjectID
from fastapi import Response


async def patch_item(request: Request, item_id: Union[ObjectID, str]) -> Response:
    original_document = await get_document(request, item_id)
    payload = getattr(request, "payload")
    now = datetime.now()
    payload["_created"] = original_document["_created"]
    payload["_updated"] = now

    try:
        document = await request.app.data.update_item(
            request.state.resource, original_document["_id"], payload
        )
    except Exception as e:
        raise e
    return Response(status_code=204)
