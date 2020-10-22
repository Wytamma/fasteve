from starlette.requests import Request
from datetime import datetime
from ..core import config
from fasteve.methods.post import post
from fasteve.methods.common import get_document
from typing import Union
from fasteve.core.utils import ObjectID


async def put_item(request: Request, item_id: Union[ObjectID, str]) -> None:
    orginal_document = await get_document(request, item_id)
    if not orginal_document:
        # insert
        response = await post(request)
        return response

    # replace
    payload = getattr(request, "payload")
    now = datetime.now()
    payload["_created"] = orginal_document["_created"]
    payload["_updated"] = now

    try:
        document = await request.app.data.replace_item(
            request.state.resource, orginal_document["_id"], payload
        )
    except Exception as e:
        raise e