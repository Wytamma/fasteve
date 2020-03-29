from starlette.requests import Request
from .methods import get, post, getitem
from fastapi import HTTPException
from .core import config
from fastapi import Depends, Path
from typing import List, Type, Callable, Union
from pydantic import BaseModel
from .schema import BaseSchema
from .resource import Resource
from .core.utils import log, ObjectID

@log
async def process_collections_request(request: Request):
    methods = {
        'GET': get, 
        'POST': post
        }
    if request.method not in methods:
        raise HTTPException(405)
    try:
        res = await methods[request.method](request)
        return res
    except Exception as e:
        raise e

def collections_endpoint_factory(resource: Resource, method: str) -> Callable:
    """Dynamically create collection endpoint with or without schema"""
    if method in ("DELETE", "HEAD"):  
        # no in_schema validation on DELETE HEAD request
        async def collections_endpoint(
            request: Request,
            ) -> dict:
            return await process_collections_request(request)   
    elif method == 'GET':
        # no in_schema validation on GET request
        # query prams
        async def collections_endpoint(
            request: Request,
            max_results: int = 25,
            page: int = 1,
            ) -> dict:
            return await process_collections_request(request)   
    else:
        if resource.bulk_inserts:
            in_schema = Union[List[resource.in_schema], resource.in_schema]
        else:
            in_schema = resource.in_schema
        async def collections_endpoint(
            request: Request, 
            in_schema:in_schema
            ) -> dict:
            request.payload = [schema.dict() for schema in in_schema] if type(in_schema) == list else in_schema.dict()
            return await process_collections_request(request)
    return collections_endpoint

async def process_item_request(request: Request):
    methods = {
        'GET': getitem, 
        }
    if request.method not in methods:
        raise HTTPException(405)
    try:
        res = await methods[request.method](request)
        return res
    except Exception as e:
        raise e

def item_endpoint_factory(resource: Resource, method: str, **kwargs) -> Callable:
    """Dynamically create item endpoint"""
    async def item_endpoint(
            request: Request,
            _id: ObjectID = Path(..., alias=f'{resource.item_name}_id')
        ) -> dict:
        request.item_id = _id
        print(vars(request))
        return await process_item_request(request)
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