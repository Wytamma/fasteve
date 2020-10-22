from starlette.requests import Request
from fasteve.core.utils import ObjectID
from typing import Union
from fasteve.methods.common import get_document
from fastapi import HTTPException

async def delete(request: Request) -> None:
    try:
        await request.app.data.remove(request.state.resource)
    except Exception as e:
        raise e


async def delete_item(request: Request, item_id: Union[ObjectID, str]) -> None:
    document = await get_document(request, item_id)
    if not document:
        raise HTTPException(404)
    try:
        await request.app.data.remove_item(
            request.state.resource, 
            document["_id"])
    except Exception as e:
        raise e
