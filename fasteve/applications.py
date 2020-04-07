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
from typing import List, Type, Optional
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
        cors_origins: List[str] = []
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
            self.register_resource(resource)
            loop = asyncio.get_event_loop()
            loop.create_task(self.create_mongo_index(resource))
            

    @log
    def register_resource(self, resource: Resource) -> None:
        # process resource_settings
        # add name to api
        router = APIRouter()

        # check response model for references 

        response_model = create_model(
            f"out_schema_{resource.name}",
            id=(ObjectID, Field(..., alias="_id")),
            updated=(datetime, Field(..., alias="_updated")),
            created=(datetime, Field(..., alias="_created")),
            __base__=resource.response_model,
        )

        ResponseModel = create_model(
            f"ResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=BaseResponseSchema,
        )

        PostResponseModel = create_model(
            f"PostResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=BaseSchema,  # No meta or links
        )
        ItemResponseModel = create_model(
            f"ItemResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=ItemBaseResponseSchema,
        )
        for method in resource.resource_methods:
            if method == "POST":
                router.add_api_route(
                    f"/{resource.name}",
                    endpoint=collections_endpoint_factory(resource, method),
                    response_model=PostResponseModel,
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
                    response_model=ResponseModel,
                    response_model_exclude_unset=True,
                    methods=[method],
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
                    response_model=ItemResponseModel,
                    response_model_exclude_unset=True,
                    methods=[method],
                )
        # TODO: api versioning
        self.include_router(
            router, tags=[str(resource.name)],
        )

    async def create_mongo_index(self, resource: Resource) -> None:
        schema = resource.schema
        for field in schema.__fields__:
            type_ = schema.__fields__[field].type_
            name = schema.__fields__[field].name
            if not is_new_type(schema.__fields__[field].type_):
                continue
            if type_.__name__ == 'Fasteve_Unique':
                collection = await self.data.motor(resource)
                res = await collection.create_index(name, unique=True)
    
    def repeat_every(
        self,
        *,
        seconds: float,
        wait_first: bool = False,
        logger: Optional[logging.Logger] = None,
        raise_exceptions: bool = False,
        max_repetitions: Optional[int] = None,
        ):
        dec2 = repeat(
                seconds=seconds,
                wait_first=wait_first,
                logger=logger,
                raise_exceptions=raise_exceptions,
                max_repetitions=max_repetitions
            )
        dec1 = self.on_event("startup")
        def merged_decorator(func):
            return dec1(dec2(func))
        return merged_decorator

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
