from starlette.requests import Request
from fasteve.core.utils import log, ObjectID
from fasteve.core import config
from math import ceil
from fastapi import HTTPException


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

    response["data"] = documents

    if config.PAGINATION:
        response["meta"] = {
            "page": page,
            "max_results": args["limit"],
            "total": count,
        }  # _meta_links(req, count)

    if config.HATEOAS:
        max_results = "&max_result=" + str(args["limit"]) if args["limit"] != 25 else ""
        response["links"] = {
            "self": {"href": request["path"], "title": request.state.resource.name},
            "parent": {"href": "/", "title": "home"},
        }  # _pagination_links(resource, req, count)
        if count > args["limit"]:
            response["links"]["next"] = {
                "href": f"{request['path']}?page={page + 1}{max_results}",
                "title": "next page",
            }
            response["links"]["last"] = {
                "href": f"{request['path']}?page={ceil(count / args['limit'])}{max_results}",
                "title": "last page",
            }
    return response


async def getitem(request: Request, item_id: ObjectID) -> dict:
    try:
        item = await request.app.data.find_one(request.state.resource, item_id)
    except Exception as e:
        raise e
    if not item:
        raise HTTPException(404)
    response = {}

    response["data"] = [item]
    return response
