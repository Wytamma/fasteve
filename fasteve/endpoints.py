from starlette.requests import Request
from .methods import get, post, get_item, delete, delete_item
from fastapi import HTTPException
from .core import config
from fastapi import Path
from typing import Callable, List, Union
from .resource import Resource
from .core.utils import log, ObjectID


@log
async def process_collections_request(request: Request) -> dict:
    methods: dict = {"GET": get, "POST": post, "DELETE": delete}
    if request.method not in methods:
        raise HTTPException(405)
    try:
        res = await methods[request.method](request)
        return res
    except Exception as e:
        raise e


def collections_endpoint_factory(resource: Resource, method: str) -> Callable:
    """Dynamically create collection endpoints"""
    if method in ("GET", "HEAD"):
        # no in_schema validation on GET request
        # query prams
        async def get_endpoint(
            request: Request, max_results: int = 25, page: int = 1,
        ) -> dict:
            return await process_collections_request(request)

        return get_endpoint

    elif method == "POST":
        if resource.bulk_inserts:
            in_schema = Union[List[resource.in_schema], resource.in_schema]  # type: ignore
        else:
            in_schema = resource.in_schema  # type: ignore

        async def post_endpoint(request: Request, in_schema: in_schema) -> dict:
            payload = (
                [dict(schema) for schema in in_schema]
                if type(in_schema) == list
                else dict(in_schema)
            )
            setattr(request, "payload", payload)
            return await process_collections_request(request)

        return post_endpoint

    elif method == "DELETE":
        # no in_schema validation on DELETE HEAD request
        async def delete_endpoint(request: Request,) -> dict:
            return await process_collections_request(request)

        return delete_endpoint

    else:
        raise Exception(f'"{method}" is an invalid HTTP method')


async def process_item_request(request: Request, item_id: ObjectID) -> dict:
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
        # no in_schema validation on GET request
        # query prams
        async def item_endpoint(
            request: Request,
            item_id: ObjectID = Path(..., alias=f"{resource.item_name}_id"),
        ) -> dict:
            return await process_item_request(request, item_id)

        return item_endpoint

    else:
        raise Exception(f'"{method}" is an invalid HTTP method')

    return item_endpoint


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
