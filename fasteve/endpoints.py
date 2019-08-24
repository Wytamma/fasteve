from starlette.requests import Request
from .methods import get
from fastapi import HTTPException
from .core import config


def collections_endpoint(request: Request) -> dict:
    # check method
    resource = request.url
    response = None
    method = request.method
    if method in ("GET", "HEAD"):
        response = get(resource) #QUERY PRAM
    else:
        raise HTTPException(405)
    # do action (method)
    # render response
    return response


def home_endpoint(request: Request) -> dict:
    response = {}
    if config.HATEOAS:
        links = []
        for resource in request.state.settings['DOMAIN'].keys():
            links.append(
                {
                    "href": f"{resource}",
                    "title": f"{resource}",
                }
            )
        response[config.LINKS] = {"child": links}
    return response

