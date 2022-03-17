from starlette.requests import Request
from fasteve.methods import delete, get, post
from fastapi import HTTPException
from fastapi import Path
from fastapi.responses import JSONResponse
from typing import Callable, Optional, Union
from fasteve.resource import Resource, SubResource
from fasteve.core.utils import log, MongoObjectId
from fasteve.endpoints.documents import process_item_request
from pymongo.errors import DuplicateKeyError, BulkWriteError
from fasteve.io.mongo.utils import render_pymongo_error


@log
async def process_subresource_request(
    request: Request, item_id: Union[MongoObjectId, str]
) -> dict:
    methods: dict = {"GET": get, "POST": post, "DELETE": delete}
    if request.method not in methods:
        raise HTTPException(405)
    try:
        res = await methods[request.method](request)
        return res
    except DuplicateKeyError as e:
        msg = render_pymongo_error(e.details)
        raise HTTPException(422, msg)
    except BulkWriteError as e:
        msg = render_pymongo_error(e.details["writeErrors"][0])
        raise HTTPException(422, msg)
    except Exception as e:
        raise e


def subresource_endpoint_factory(
    resource: Resource, method: str, subresource: SubResource
) -> Callable:
    # i may have to pass lookup all the way down
    # i think that's okay as I'll have to do it anyway for aggergation

    if method in ("GET", "HEAD"):  # not sure why this...
        # no model validation on GET request
        if resource.alt_id:

            async def subresource_endpoint_with_alt_id(
                request: Request,
                item_id: Union[MongoObjectId, int, str] = Path(
                    ..., alias=f"{resource.item_name}_id"
                ),
            ) -> dict:
                return await process_subresource_request(request, item_id)

            return subresource_endpoint_with_alt_id
        else:

            async def subresource_endpoint(
                request: Request,
                item_id: Union[MongoObjectId, int] = Path(
                    ..., alias=f"{resource.item_name}_id"
                ),
            ) -> Optional[dict]:
                return await process_item_request(request, item_id)

            return subresource_endpoint

    else:
        raise Exception(f'"{method}" is an invalid HTTP method')


async def home_endpoint(request: Request) -> JSONResponse:
    response = {}
    if request.app.config.HATEOAS:  # move to repare response function
        links = []
        for resource in request.app.resources:
            links.append({"href": f"/{resource.name}", "title": f"{resource.name}"})
        response[request.app.config.LINKS] = {"child": links}
    return JSONResponse(content=response)
