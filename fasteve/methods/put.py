from starlette.requests import Request
from fasteve.methods.post import post
from fasteve.methods.common import get_item_internal
from typing import Union
from fasteve.core.utils import MongoObjectId
from fastapi import Response
from sqlmodel.main import SQLModelMetaclass


async def put_item(request: Request, item_id: Union[MongoObjectId, int, str]) -> Response:
    """Upsert"""
    original_item = await get_item_internal(request, item_id)
    payload = getattr(request, "payload")

    pk = None
    if type(request.state.resource.model) == SQLModelMetaclass:
        pk = request.state.resource.model.get_primary_key()
    elif MongoObjectId.is_valid(item_id):
        pk = '_id'

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
            request.state.resource, {pk:item_id}, payload
        )
    except Exception as e:
        raise e
    return Response(status_code=204)
