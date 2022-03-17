from starlette.requests import Request
from fasteve.methods import delete, get, post
from fastapi import HTTPException
from typing import Callable, List, Union
from fasteve.resource import Resource
from fasteve.core.utils import log
from pymongo.errors import DuplicateKeyError, BulkWriteError
from fasteve.io.mongo.utils import render_pymongo_error


@log
async def process_collections_request(request: Request) -> dict:
    methods: dict = {"GET": get, "POST": post, "DELETE": delete}
    if request.method not in methods:
        raise HTTPException(405)
    try:
        res = await methods[request.method](request)
        return res
    except DuplicateKeyError as e:  # TODO: move these errors into the datalayer and catch a general Fasteve.DatabaseError
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
        # no model validation on GET request
        # query prams
        async def get_endpoint(
            request: Request, max_results: int = 25, page: int = 1, embedded: str = "{}"
        ) -> dict:
            response = await process_collections_request(request)
            await request.app.events.run("after_read_resource", resource.name, response)
            return response

        return get_endpoint

    elif method == "POST":
        if resource.bulk_create:
            model = Union[List[resource.create_model], resource.create_model]  # type: ignore
        else:
            model = resource.create_model  # type: ignore

        async def post_endpoint(request: Request, model: model) -> dict:
            payload = (
                [model.dict() for model in model]  # type: ignore
                if type(model) == list
                else [model.dict()]  # type: ignore
            )

            setattr(request, "payload", payload)
            await request.app.events.run("before_create_items", resource.name, payload)
            response = await process_collections_request(request)
            await request.app.events.run("after_create_items", resource.name, response)
            return response

        return post_endpoint

    elif method == "DELETE":
        # no model validation on DELETE HEAD request
        async def delete_endpoint(
            request: Request,
        ) -> dict:
            return await process_collections_request(request)

        return delete_endpoint

    else:
        raise Exception(f'"{method}" is an invalid HTTP method')
