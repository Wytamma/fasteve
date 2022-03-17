from starlette.requests import Request
from fasteve.core.utils import (
    InvalidMongoObjectId,
    log,
    MongoObjectId,
)
from math import ceil
from fastapi import HTTPException
from typing import Union
import json

from fasteve.methods.common import get_item_internal


@log
async def get(request: Request) -> dict:
    resource = request.state.resource
    query_params = dict(request.query_params)
    path_params = dict(request.path_params)
    limit = int(query_params["max_results"]) if "max_results" in query_params else 25
    page = int(query_params["page"]) if "page" in query_params else 1
    skip = (page - 1) * limit if page > 1 else 0

    query = {}
    pipeline = []

    item_id = (
        path_params[f"{resource.item_name}_id"]
        if f"{resource.item_name}_id" in path_params
        else None
    )
    if item_id:
        # subresource
        subresource_path_name = request.url.path.split("/")[-1]
        sub_resource = next(
            (
                resource
                for resource in resource.sub_resources
                if resource.name == subresource_path_name
            ),
            None,
        )
        if not sub_resource:
            raise HTTPException(404)
        try:
            query[sub_resource.id_field] = MongoObjectId.validate(item_id)
        except InvalidMongoObjectId:
            lookup = {}
            lookup["from"] = resource.name
            lookup["localField"] = sub_resource.id_field
            lookup["foreignField"] = "_id"
            lookup["as"] = sub_resource.id_field
            pipeline.append({"$lookup": lookup})
            pipeline.append({"$unwind": "$" + sub_resource.id_field})
            pipeline.append(
                {"$match": {f"{sub_resource.id_field}.{resource.alt_id}": item_id}}
            )
            pipeline.append(
                {"$addFields": {sub_resource.id_field: f"${sub_resource.id_field}._id"}}
            )

        resource = sub_resource.resource
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

    for field_name in embedded:
        if not embedded[field_name]:
            continue
        try:
            field = resource.response_model.__fields__[field_name]
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
            resource, pipline=pipeline, skip=skip, limit=limit
        )
    else:
        try:
            documents, count = await request.app.data.find(
                resource, query=query, skip=skip, limit=limit
            )
        except Exception as e:
            raise e
    response = {}

    response[request.app.config.DATA] = documents

    if request.app.config.PAGINATION:
        response[request.app.config.META] = {
            "page": page,
            "max_results": limit,
            "total": count,
        }  # _meta_links(req, count)

    if request.app.config.HATEOAS:
        max_results = "&max_result=" + str(limit) if limit != 25 else ""
        response[request.app.config.LINKS] = {
            "self": {"href": request["path"], "title": resource.name},
            "parent": {"href": "/", "title": "home"},
        }  # _pagination_links(resource, req, count)
        if count > limit:
            response[request.app.config.LINKS]["next"] = {
                "href": f"{request['path']}?page={page + 1}{max_results}",
                "title": "next page",
            }
            response[request.app.config.LINKS]["last"] = {
                "href": f"{request['path']}?page={ceil(count / limit)}{max_results}",
                "title": "last page",
            }
    return response


async def get_item(request: Request, item_id: Union[MongoObjectId, int, str]) -> dict:

    try:
        item = await get_item_internal(request, item_id)
    except InvalidMongoObjectId as e:
        raise HTTPException(400, str(e))

    if not item:
        raise HTTPException(404)
    response = {}
    response[request.app.config.DATA] = [item]
    return response
