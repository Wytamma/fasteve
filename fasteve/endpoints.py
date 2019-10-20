from starlette.requests import Request
from .methods import get, post
from fastapi import HTTPException
from .core import config
from fastapi import Depends
from typing import List, Type, Callable
from pydantic import BaseModel
from .schema import BaseSchema
from .resource import Resource
from .core.utils import log

@log
async def process_collections_request(request: Request):
    methods = {'GET': get, 'POST': post}
    try:
        res = await methods[request.method](request)
        return res
    except:
        HTTPException(405)

def collections_endpoint_factory(resource: Resource, method: str) -> Callable:
    """Dynamically create collection endpoint with or without schema"""
    if method in ("GET", "DELETE", "HEAD"):  # no in_schema validation on GET DELETE HEAD request
        async def collections_endpoint(request: Request) -> dict:
            return await process_collections_request(request)
    else:
        async def collections_endpoint(request: Request, in_schema:resource.in_schema) -> dict:
            request.payload = dict(in_schema)
            return await process_collections_request(request)
    return collections_endpoint

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
    if config.HATEOAS:  # move to repare response function
        links = []
        for resource in request.app.resources:
            links.append({"href": f"/{resource.name}", "title": f"{resource.name}"})
        response[config.LINKS] = {"child": links}
    return response