from starlette.requests import Request
from fasteve.core.utils import ObjectID
from typing import Union
from fasteve.methods.common import get_document
from fastapi import HTTPException
from fastapi import Response


async def delete(request: Request) -> Response:
    try:
        await request.app.data.remove(request.state.resource)
    except Exception as e:
        raise e
    return Response(status_code=204)


async def delete_item(request: Request, item_id: Union[ObjectID, str]) -> Response:
    document = await get_document(request, item_id)
    if not document:
        raise HTTPException(404)
    try:
        await request.app.data.remove_item(request.state.resource, document["_id"])
    except Exception as e:
        raise e
    return Response(status_code=204)
