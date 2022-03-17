from starlette.requests import Request
from datetime import datetime
from fasteve.methods.common import get_item_internal
from typing import Union
from fasteve.core.utils import MongoObjectId
from fastapi import HTTPException, Response
from sqlmodel.main import SQLModelMetaclass

async def patch_item(request: Request, item_id: Union[MongoObjectId, int, str]) -> Response:
    original_document = await get_item_internal(request, item_id)
    if not original_document:
        raise HTTPException(404)
    payload = getattr(request, "payload")
    pk = None
    if type(request.state.resource.model) == SQLModelMetaclass:
        pk = request.state.resource.model.get_primary_key()
    elif MongoObjectId.is_valid(item_id):
        pk = '_id'

    try:
        document = await request.app.data.update_item(
            request.state.resource, {pk: item_id}, payload
        )
    except Exception as e:
        raise e
    return Response(status_code=204)
