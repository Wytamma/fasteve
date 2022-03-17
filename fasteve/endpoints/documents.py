from starlette.requests import Request
from fasteve.methods import delete_item, get_item, patch_item, put_item
from fastapi import HTTPException
from fastapi import Path
from typing import Callable, Optional, Union
from fasteve.resource import Resource
from fasteve.core.utils import MongoObjectId
from pymongo.errors import DuplicateKeyError, BulkWriteError
from fasteve.io.mongo.utils import render_pymongo_error


async def process_item_request(
    request: Request, item_id: Union[MongoObjectId, str, int]
) -> Optional[dict]:
    methods = {
        "GET": get_item,
        "DELETE": delete_item,
        "PUT": put_item,
        "PATCH": patch_item,
    }
    if request.method not in methods:
        raise HTTPException(405)
    try:
        res = await methods[request.method](request, item_id)
    except DuplicateKeyError as e:
        msg = render_pymongo_error(e.details)
        raise HTTPException(422, msg)
    except BulkWriteError as e:
        msg = render_pymongo_error(e.details["writeErrors"][0])
        raise HTTPException(422, msg)
    except Exception as e:
        raise e
    return res  # type: ignore


def item_endpoint_factory(resource: Resource, method: str) -> Callable:
    """Dynamically create item endpoint"""

    if method in ("GET", "HEAD", "DELETE"):
        # no model validation on GET request
        # TODO: DELETE needs if-match header?
        if resource.alt_id:

            async def item_endpoint_with_alt_id(
                request: Request,
                item_id: Union[MongoObjectId, str, int] = Path(
                    ..., alias=f"{resource.item_name}_id"
                ),
            ) -> Optional[dict]:
                return await process_item_request(request, item_id)

            return item_endpoint_with_alt_id
        else:

            async def item_endpoint(
                request: Request,
                item_id: Union[MongoObjectId, int] = Path(
                    ..., alias=f"{resource.item_name}_id"
                ),
            ) -> Optional[dict]:
                response = await process_item_request(request, item_id)
                await request.app.events.run("after_read_item", resource.name, response)
                return response

            return item_endpoint
    elif method in ["PUT", "PATCH"]:
        model = resource.create_model
        if method == "PATCH":
            model = resource.update_model
        if resource.alt_id:
            # TODO: REFACTOR
            async def modify_item_endpoint_with_alt_id(
                request: Request,
                model: model,  # type: ignore
                item_id: Union[MongoObjectId, str, int] = Path(
                    ..., alias=f"{resource.item_name}_id"
                ),
            ) -> Optional[dict]:
                setattr(request, "payload", model.dict(exclude_unset=True))  # type: ignore
                return await process_item_request(request, item_id)

            return modify_item_endpoint_with_alt_id
        else:

            async def modify_item_endpoint(
                request: Request,
                model: model,  # type: ignore
                item_id: Union[MongoObjectId, int] = Path(
                    ..., alias=f"{resource.item_name}_id"
                ),
            ) -> Optional[dict]:
                setattr(request, "payload", model.dict(exclude_unset=True))  # type: ignore
                return await process_item_request(request, item_id)

            return modify_item_endpoint
    else:
        raise Exception(f'"{method}" is an invalid HTTP method')

    return item_endpoint
