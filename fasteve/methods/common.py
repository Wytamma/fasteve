from starlette.requests import Request
from fasteve.core.utils import ObjectID
from typing import Union
from fastapi import HTTPException


async def get_document(request: Request, item_id: Union[ObjectID, str]) -> dict:
    try:
        query = {"_id": ObjectID.validate(item_id)}
    except ValueError:
        # item_id is not a valid ObjectID check if there is an alt_id set
        if not request.state.resource.alt_id:
            raise HTTPException(
                404, "The ObjectID is invaild and there is no alternative ID"
            )
        query = {request.state.resource.alt_id: item_id}
    try:
        document = await request.app.data.find_one(request.state.resource, query)
    except Exception as e:
        raise e
    return document
