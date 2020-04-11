from fastapi import FastAPI, APIRouter
from .middleware.resource import ResourceMiddleware
from .middleware.cors import CORSMiddleware
from .endpoints import (
    collections_endpoint_factory,
    home_endpoint,
    item_endpoint_factory,
)
from .core import config
from .schema import BaseResponseSchema, BaseSchema, ItemBaseResponseSchema
from typing import List, Type, Optional, Union
from types import ModuleType
from .resource import Resource
from .io.mongo import Mongo, MongoClient
from .io.base import DataLayer
from .core.utils import log, ObjectID, is_new_type, repeat_every as repeat
from datetime import datetime
from pydantic import Field, create_model
import asyncio
import logging


class Fasteve(FastAPI):
    def __init__(
        self,
        resources: List[Resource] = [],
        data: Type[DataLayer] = Mongo,
        cors_origins: List[str] = [],
    ) -> None:

        super().__init__()  # Initialise FastAPI super class

        # set defaults
        self.cors_origins = cors_origins
        # validate user settings
        self.resources = resources

        self._validate_config(config)
        self.config = config

        self._register_resource_middleware()
        self._register_CORS_middleware()

        self._register_home_endpoint()

        # connect to db
        MongoClient.connect()

        self.add_event_handler(
            "shutdown", MongoClient.close
        )  # this can't be in the application layer i.e. needs to come from data layer

        self.data = data(app=self)  # eve pattern

        for resource in self.resources:
            # create indexes
            self.create_mongo_index(resource)

        for resource in self.resources:
            # create endpoints
            self.register_resource(resource)

    @log
    def register_resource(self, resource: Resource) -> None:
        print(f"Registering Resource: {resource.name}")
        # process resource_settings
        # add name to api
        router = APIRouter()

        # check models for data relations
        resource.schema = self._embed_data_relation(resource.schema)
        resource.response_model = self._embed_data_relation(
            resource.response_model, response=True
        )

        response_model = self._prepare_response_model(
            resource.response_model, resource.name
        )

        Response = create_model(
            f"ResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=BaseResponseSchema,
        )

        PostResponse = create_model(
            f"PostResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=BaseSchema,  # No meta or links
        )

        for method in resource.resource_methods:
            if method == "POST":
                router.add_api_route(
                    f"/{resource.name}",
                    endpoint=collections_endpoint_factory(resource, method),
                    response_model=PostResponse,
                    response_model_exclude_unset=True,
                    methods=[method],
                    status_code=201,
                )
            elif method == "DELETE":
                router.add_api_route(
                    f"/{resource.name}",
                    endpoint=collections_endpoint_factory(resource, method),
                    methods=[method],
                    status_code=204,
                )
            else:
                router.add_api_route(
                    f"/{resource.name}",
                    endpoint=collections_endpoint_factory(resource, method),
                    response_model=Response,
                    response_model_exclude_unset=True,
                    methods=[method],
                )

        ItemResponse = create_model(
            f"ItemResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=ItemBaseResponseSchema,
        )

        for method in resource.item_methods:
            if method == "DELETE":
                router.add_api_route(
                    f"/{resource.name}/{{{str(resource.item_name) + '_id'}}}",
                    endpoint=item_endpoint_factory(resource, method),
                    methods=[method],
                    status_code=204,
                )
            else:
                router.add_api_route(
                    f"/{resource.name}/{{{str(resource.item_name) + '_id'}}}",
                    endpoint=item_endpoint_factory(resource, method),
                    response_model=ItemResponse,
                    response_model_exclude_unset=True,
                    methods=[method],
                )
        # TODO: api versioning
        self.include_router(
            router, tags=[str(resource.name)],
        )

    async def _create_mongo_index_internal(self, resource, field_name) -> None:
        collection = await self.data.motor(resource)
        res = await collection.create_index(field_name, unique=True)
        print(f"Created unique index for {field_name} in {resource.name}")

    def create_mongo_index(self, resource: Resource) -> None:
        fields = resource.schema.__fields__
        for name in fields:
            field = fields[name]
            type_ = field.type_
            if not is_new_type(type_):
                continue
            if type_.__name__ == "Fasteve_Unique":
                asyncio.create_task(self._create_mongo_index_internal(resource, name))

    def repeat_every(
        self,
        *,
        seconds: float,
        wait_first: bool = False,
        logger: Optional[logging.Logger] = None,
        raise_exceptions: bool = False,
        max_repetitions: Optional[int] = None,
    ):
        """https://stackoverflow.com/a/52518284/5209891"""
        dec2 = repeat(
            seconds=seconds,
            wait_first=wait_first,
            logger=logger,
            raise_exceptions=raise_exceptions,
            max_repetitions=max_repetitions,
        )
        dec1 = self.on_event("startup")

        def merged_decorator(func):
            return dec1(dec2(func))

        return merged_decorator

    def _embed_data_relation(self, model, response=False):

        fields = model.__fields__.keys()
        for name in fields:
            field = model.__fields__[name]

            if not "data_relation" in field.field_info.extra:
                continue

            data_relation = field.field_info.extra["data_relation"]
            outer_type_ = field.outer_type_
            many = False

            if outer_type_ not in (ObjectID, List[ObjectID]):
                raise ValueError(
                    f"Data relation ({model.__name__}: {name}) must be must be type ObjectID or List[ObjectID]"
                )

            if response:
                response_model = self._prepare_response_model(
                    data_relation.response_model, data_relation.name + "_embedded"
                )  # add ids, create, updated, ect
                if outer_type_ == ObjectID:
                    type_ = Union[outer_type_, response_model]
                else:
                    type_ = Union[outer_type_, List[response_model]]
                    many = True
            else:
                type_ = outer_type_

            if field.required:
                relation_field = {
                    name: (type_, Field(..., data_relation=data_relation, many=many))
                }
            else:
                relation_field = {
                    name: (type_, Field(None, data_relation=data_relation, many=many))
                }

            # relation_field = {name:(type_,field)}
            model = create_model(model.__name__, **relation_field, __base__=model)
        return model

    def _prepare_response_model(self, response_model, name):
        return create_model(
            f"out_schema_{name}",
            id=(ObjectID, Field(..., alias="_id")),
            updated=(datetime, Field(..., alias="_updated")),
            created=(datetime, Field(..., alias="_created")),
            __base__=response_model,
        )

    def _register_home_endpoint(self) -> None:
        self.add_api_route(f"/", home_endpoint)

    def _register_resource_middleware(self) -> None:
        """Pass resources to every request"""
        # app is already passed to every request!
        # therfore I can use request.app.resources
        self.add_middleware(ResourceMiddleware, resources=self.resources)

    def _register_CORS_middleware(self) -> None:
        """Set global Cross-Origin Resource Sharing"""
        if self.cors_origins:
            # app level cors
            origins_raw = self.cors_origins
        elif config.CORS_ORIGINS:
            # global cors
            origins_raw = config.CORS_ORIGINS.split(",")
        # CORS
        origins = []
        # Set all CORS enabled origins
        if config.CORS_ORIGINS:
            for origin in origins_raw:
                use_origin = origin.strip()
                origins.append(use_origin)
            self.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def _validate_config(self, config: ModuleType) -> None:
        # raise errors if config is invalid
        pass
