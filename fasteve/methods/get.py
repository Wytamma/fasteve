from starlette.requests import Request
from fasteve.core.utils import log, ObjectID
from fasteve.core import config
from math import ceil
from fastapi import HTTPException
from typing import Union


@log
async def get(request: Request) -> dict:

    query_params = dict(request.query_params)
    args = dict()

    args["limit"] = (
        int(query_params["max_results"]) if "max_results" in query_params else 25
    )
    page = int(query_params["page"]) if "page" in query_params else 1
    args["skip"] = (page - 1) * args["limit"] if page > 1 else 0

    try:
        documents, count = await request.app.data.find(request.state.resource, args)
    except Exception as e:
        raise e

    response = {}

    response[config.DATA] = documents

    if config.PAGINATION:
        response[config.META] = {
            "page": page,
            "max_results": args["limit"],
            "total": count,
        }  # _meta_links(req, count)

    if config.HATEOAS:
        max_results = "&max_result=" + str(args["limit"]) if args["limit"] != 25 else ""
        response[config.LINKS] = {
            "self": {"href": request["path"], "title": request.state.resource.name},
            "parent": {"href": "/", "title": "home"},
        }  # _pagination_links(resource, req, count)
        if count > args["limit"]:
            response[config.LINKS]["next"] = {
                "href": f"{request['path']}?page={page + 1}{max_results}",
                "title": "next page",
            }
            response[config.LINKS]["last"] = {
                "href": f"{request['path']}?page={ceil(count / args['limit'])}{max_results}",
                "title": "last page",
            }
    return response


async def get_item(request: Request, item_id: Union[ObjectID, str]) -> dict:
    try:
        lookup = {"_id": ObjectID.validate(item_id)}
    except ValueError:
        lookup = {request.state.resource.alt_id: item_id}
    try:
        item = await request.app.data.find_one(request.state.resource, lookup)
    except Exception as e:
        raise e
    if not item:
        raise HTTPException(404)
    response = {}

    response[config.DATA] = [item]
    return response
