from starlette.requests import Request
from .methods import get, post, get_item, delete, delete_item
from fastapi import HTTPException
from .core import config
from fastapi import Path
from typing import Callable, List, Union
from .resource import Resource
from .core.utils import log, ObjectID
from pymongo.errors import DuplicateKeyError, BulkWriteError
from .utils import SubResource


def render_pymongo_error(details):
    key = list(details["keyValue"].keys())[0]
    val = details["keyValue"][key]
    msg = {
        "loc": ["body", "schema", key],
        "msg": f"value '{val}' is not unique",
        "type": "value_error.not_unique",
    }
    return msg


@log
async def process_collections_request(request: Request) -> dict:
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


def collections_endpoint_factory(resource: Resource, method: str) -> Callable:
    """Dynamically create collection endpoints"""
    if method in ("GET", "HEAD"):
        # no schema validation on GET request
        # query prams
        async def get_endpoint(
            request: Request, max_results: int = 25, page: int = 1, embedded: str = "{}"
        ) -> dict:
            return await process_collections_request(request)

        return get_endpoint

    elif method == "POST":
        if resource.bulk_inserts:
            schema = Union[List[resource.schema], resource.schema]  # type: ignore
        else:
            schema = resource.schema  # type: ignore

        async def post_endpoint(request: Request, schema: schema) -> dict:
            payload = (
                [schema.dict() for schema in schema]
                if type(schema) == list
                else schema.dict()
            )
            setattr(request, "payload", payload)
            return await process_collections_request(request)

        return post_endpoint

    elif method == "DELETE":
        # no schema validation on DELETE HEAD request
        async def delete_endpoint(request: Request,) -> dict:
            return await process_collections_request(request)

        return delete_endpoint

    else:
        raise Exception(f'"{method}" is an invalid HTTP method')


async def process_item_request(request: Request, item_id: Union[ObjectID, str]) -> dict:
    methods = {"GET": get_item, "DELETE": delete_item}
    if request.method not in methods:
        raise HTTPException(405)
    try:
        res = await methods[request.method](request, item_id)  # type: ignore # this is giving a mypy error because of mixed return types
        return res
    except Exception as e:
        raise e


def item_endpoint_factory(resource: Resource, method: str) -> Callable:
    """Dynamically create item endpoint"""

    if method in ("GET", "HEAD", "DELETE"):
        # no schema validation on GET request
        if resource.alt_id:

            async def item_endpoint_with_alt_id(
                request: Request,
                item_id: Union[ObjectID, str] = Path(
                    ..., alias=f"{resource.item_name}_id"
                ),
            ) -> dict:
                return await process_item_request(request, item_id)

            return item_endpoint_with_alt_id
        else:

            async def item_endpoint(
                request: Request,
                item_id: ObjectID = Path(..., alias=f"{resource.item_name}_id"),
            ) -> dict:
                return await process_item_request(request, item_id)

            return item_endpoint

    else:
        raise Exception(f'"{method}" is an invalid HTTP method')

    return item_endpoint


@log
async def process_subresource_request(request: Request, item_id) -> dict:
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
        # no schema validation on GET request
        if resource.alt_id:

            async def subresource_endpoint_with_alt_id(
                request: Request,
                item_id: Union[ObjectID, str] = Path(
                    ..., alias=f"{resource.item_name}_id"
                ),
            ) -> dict:
                return await process_subresource_request(request, item_id)

            return subresource_endpoint_with_alt_id
        else:

            async def subresource_endpoint(
                request: Request,
                item_id: ObjectID = Path(..., alias=f"{resource.item_name}_id"),
            ) -> dict:
                return await process_item_request(request, item_id)

            return subresource_endpoint

    else:
        raise Exception(f'"{method}" is an invalid HTTP method')


def home_endpoint(request: Request) -> dict:
    response = {}
    if config.HATEOAS:  # move to repare response function
        links = []
        for resource in request.app.resources:
            links.append({"href": f"/{resource.name}", "title": f"{resource.name}"})
        response[config.LINKS] = {"child": links}
    return response


def me_endpoint(request: Request) -> dict:
    """for auth / user info"""
    response = {}
    if config.HATEOAS:  # move to prepare response function
        links = []
        for resource in request.app.resources:
            links.append({"href": f"/{resource.name}", "title": f"{resource.name}"})
        response[config.LINKS] = {"child": links}
    return response
