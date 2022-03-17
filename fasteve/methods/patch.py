from starlette.requests import Request
from fasteve.methods.common import get_item_internal
from typing import Union
from fasteve.core.utils import MongoObjectId
from fastapi import HTTPException, Response


async def patch_item(
    request: Request, item_id: Union[MongoObjectId, int, str]
) -> Response:
    original_document = await get_item_internal(request, item_id)
    if not original_document:
        raise HTTPException(404)
    payload = getattr(request, "payload")
    pk = request.state.resource.model.get_primary_key()
    if pk == "_id":
        MongoObjectId.validate(item_id)
    query = {pk: item_id}

    try:
        document = await request.app.data.update_item(
            request.state.resource, query, payload
        )
    except Exception as e:
        raise e
    return Response(status_code=204)
