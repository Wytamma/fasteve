from starlette.requests import Request
from fasteve.core.utils import (
    MongoObjectId,
)
from typing import Union
from fasteve.methods.common import get_item_internal
from fastapi import HTTPException
from fastapi import Response


async def delete(request: Request) -> Response:
    try:
        await request.app.data.remove(request.state.resource)
    except Exception as e:
        raise e
    return Response(status_code=204)


async def delete_item(
    request: Request, item_id: Union[MongoObjectId, int, str]
) -> Response:
    item = await get_item_internal(request, item_id)
    if not item:
        raise HTTPException(404)
    pk = request.state.resource.model.get_primary_key()
    if pk == "_id":
        MongoObjectId.validate(item_id)
    query = {pk: item_id}
    try:
        await request.app.data.remove_item(request.state.resource, query)
    except Exception as e:
        raise e
    return Response(status_code=204)
