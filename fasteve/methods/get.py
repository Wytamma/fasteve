from starlette.requests import Request
from fasteve.core.utils import log, ObjectID
from fasteve.core import config
from math import ceil
from fastapi import HTTPException
from typing import Union
import json


@log
async def get(request: Request) -> dict:

    query_params = dict(request.query_params)

    limit = int(query_params["max_results"]) if "max_results" in query_params else 25
    page = int(query_params["page"]) if "page" in query_params else 1
    skip = (page - 1) * limit if page > 1 else 0

    try:
        if "embedded" in query_params and query_params["embedded"]:
            embedded = json.loads(query_params["embedded"])
        else:
            embedded = {}
    except:
        detail = [
            {
                "loc": ["query", "embedded"],
                "msg": "value is not a valid dict",
                "type": "type_error.dict",
            }
        ]
        raise HTTPException(422, detail)

    pipeline = []
    for field_name in embedded:
        if not embedded[field_name]:
            continue
        try:
            field = request.state.resource.response_model.__fields__[field_name]
        except:
            detail = [
                {
                    "loc": ["query", "embedded"],
                    "msg": f"field '{field_name}' is not valid",
                    "type": "value_error.not_valid",
                }
            ]
            raise HTTPException(422, detail)
        try:
            field.field_info.extra["data_relation"]
        except:
            detail = [
                {
                    "loc": ["query", "embedded"],
                    "msg": f"field '{field_name}' is not a embedable",
                    "type": "value_error.not_embedable",
                }
            ]
            raise HTTPException(422, detail)
        lookup = {}
        lookup["from"] = field_name
        lookup["localField"] = field_name
        lookup["foreignField"] = "_id"
        lookup["as"] = field_name
        stage = {"$lookup": lookup}
        pipeline.append(stage)  # assumes valid
        if not field.field_info.extra["many"]:
            pipeline.append({"$unwind": "$" + field_name})
    if pipeline:
        documents, count = await request.app.data.aggregate(
            request.state.resource, pipline=pipeline, skip=skip, limit=limit
        )
    else:
        try:
            documents, count = await request.app.data.find(
                request.state.resource, skip=skip, limit=limit
            )
        except Exception as e:
            raise e

    response = {}

    response[config.DATA] = documents

    if config.PAGINATION:
        response[config.META] = {
            "page": page,
            "max_results": limit,
            "total": count,
        }  # _meta_links(req, count)

    if config.HATEOAS:
        max_results = "&max_result=" + str(limit) if limit != 25 else ""
        response[config.LINKS] = {
            "self": {"href": request["path"], "title": request.state.resource.name},
            "parent": {"href": "/", "title": "home"},
        }  # _pagination_links(resource, req, count)
        if count > limit:
            response[config.LINKS]["next"] = {
                "href": f"{request['path']}?page={page + 1}{max_results}",
                "title": "next page",
            }
            response[config.LINKS]["last"] = {
                "href": f"{request['path']}?page={ceil(count / limit)}{max_results}",
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
