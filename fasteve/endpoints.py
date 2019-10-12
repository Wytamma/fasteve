from starlette.requests import Request
from .methods import get
from fastapi import HTTPException
from .core import config


def collections_endpoint(request: Request) -> dict:
    # check method
    request.url
    print(dir(request))
    response = None
    method = request.method
    allowed_methods = ["GET", "HEAD"]  # load this on a per resource basis
    # do action (method)
    if method not in allowed_methods:
        raise HTTPException(405)
    if method in ("GET", "HEAD"):
        response = get(request)  # QUERY PRAM
    else:
        raise HTTPException(405)
    # render response
    return response


def home_endpoint(request: Request) -> dict:
    response = {}
    if config.HATEOAS:  # move to repare reponse function
        links = []
        for resource in request.state.resources:
            links.append({"href": f"{resource.route}", "title": f"{resource.route}"})
        response[config.LINKS] = {"child": links}
    return response
