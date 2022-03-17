from starlette.requests import Request
from fasteve.core.utils import (
    InvalidMongoObjectId,
    MongoObjectId,
)
from typing import Union
from sqlmodel.main import SQLModelMetaclass


async def get_item_internal(
    request: Request, item_id: Union[MongoObjectId, int, str]
) -> dict:
    pk = request.state.resource.model.get_primary_key()
    if type(request.state.resource.model) == SQLModelMetaclass:
        query = {pk: item_id}
    else:
        try:
            query = {pk: MongoObjectId.validate(item_id)}
        except InvalidMongoObjectId as e:
            # item_id is not a valid MongoObjectId check if there is an alt_id set
            if not request.state.resource.alt_id:
                raise e
            query = {request.state.resource.alt_id: item_id}
    try:
        document = await request.app.data.find_one(request.state.resource, query)
    except Exception as e:
        raise e
    return document
