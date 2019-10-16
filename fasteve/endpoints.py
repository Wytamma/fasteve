from starlette.requests import Request
from .methods import get
from fastapi import HTTPException
from .core import config
from fastapi import Depends
from typing import List, Type, Callable
from pydantic import BaseModel
from .schema import BaseSchema
from .resource import Resource
from .core.utils import log


async def process_collections_request(request: Request, resource: Resource):
    methods = {'GET': get, 'POST': get}
    try:
        res = await methods[request.method](request)
        return res
    except:
        HTTPException(405)

def collections_endpoint_factory(resource: Resource, method: str) -> Callable:
    """dynamicly create collection endpoint with or without schema"""
    if method in ("GET", "DELETE"):  # no in_schema validation on GET DELETE request
        async def collections_endpoint(request: Request) -> dict:
            return await process_collections_request(request, resource)
    else:
        async def collections_endpoint(request: Request, in_schema:resource.in_schema or resource.schema) -> dict:
            return await process_collections_request(request, resource)
    return collections_endpoint

def home_endpoint(request: Request) -> dict:
    response = {}
    if config.HATEOAS:  # move to repare reponse function
        links = []
        for resource in request.app.resources:
            links.append({"href": f"/{resource.route}", "title": f"{resource.route}"})
        response[config.LINKS] = {"child": links}
    return response


def me_endpoint(request: Request) -> dict:
    """for auth / user info"""
    response = {}
    if config.HATEOAS:  # move to repare reponse function
        links = []
        for resource in request.app.resources:
            links.append({"href": f"/{resource.route}", "title": f"{resource.route}"})
        response[config.LINKS] = {"child": links}
    return response