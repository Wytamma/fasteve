from fastapi import FastAPI, APIRouter
from .middleware.resource import ResourceMiddleware
from .middleware.cors import CORSMiddleware
from .endpoints import (
    collections_endpoint_factory,
    home_endpoint,
    item_endpoint_factory,
)
from .core import config
from .schema import BaseResponseSchema, BaseSchema
from typing import List, Type
from types import ModuleType
from .resource import Resource
from .io.mongo import Mongo, MongoClient
from .io.base import DataLayer
from .core.utils import log, ObjectID
from datetime import datetime
from pydantic import Field, create_model


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
        self.config = self._validate_config(config)

        self._register_resource_middleware()
        self._register_CORS_middleware()

        self._register_home_endpoint()

        self.add_event_handler(
            "startup", MongoClient.connect
        )  # this can't be in the application layer i.e. needs to come from data layer
        self.add_event_handler(
            "shutdown", MongoClient.close
        )  # this can't be in the application layer i.e. needs to come from data layer

        self.data = data(app=self)  # eve pattern

        for resource in self.resources:
            self.register_resource(resource)

    @log
    def register_resource(self, resource: Resource) -> None:
        # process resource_settings
        # add name to api
        router = APIRouter()
        out_schema = create_model(
            f"out_schema_{resource.name}",
            id=(ObjectID, Field(..., alias="_id")),
            updated=(datetime, Field(..., alias="_updated")),
            created=(datetime, Field(..., alias="_created")),
            __base__=resource.response_model,
        )

        ResponseModel = create_model(
            f"ResponseSchema_{resource.name}",
            data=(List[out_schema], ...),  # type: ignore
            __base__=BaseResponseSchema,
        )
        PostResponseModel = create_model(
            f"PostResponseSchema_{resource.name}",
            data=(List[out_schema], ...),  # type: ignore
            __base__=BaseSchema,  # No meta or links
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
                    response_model=ResponseModel,
                    response_model_exclude_unset=True,
                    methods=[method],
                )
        # TODO: api versioning
        self.include_router(
            router, tags=[str(resource.name)],
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
        elif self.config.CORS_ORIGINS:
            # global cors
            origins_raw = self.config.CORS_ORIGINS.split(",")
        # CORS
        origins = []
        # Set all CORS enabled origins
        if self.config.CORS_ORIGINS:
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

    def _validate_config(self, config: ModuleType) -> ModuleType:
        # raise errors if config is invalid
        return config
