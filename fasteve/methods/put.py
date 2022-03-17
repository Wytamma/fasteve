from starlette.requests import Request
from fasteve.methods.post import post
from fasteve.methods.common import get_item_internal
from typing import Union
from fasteve.core.utils import MongoObjectId
from fastapi import Response


async def put_item(
    request: Request, item_id: Union[MongoObjectId, int, str]
) -> Response:
    """Upsert"""
    original_item = await get_item_internal(request, item_id)
    payload = getattr(request, "payload")

    pk = request.state.resource.model.get_primary_key()
    if pk == "_id":
        MongoObjectId.validate(item_id)
    query = {pk: item_id}

    if not original_item:
        # create
        if pk:
            payload[pk] = item_id
        # if it is not valid must be an alt_id
        setattr(request, "payload", [payload])  # post expects a list
        await post(request)
        return Response(status_code=204)

    # replace
    try:
        document = await request.app.data.replace_item(
            request.state.resource, query, payload
        )
    except Exception as e:
        raise e
    return Response(status_code=204)
