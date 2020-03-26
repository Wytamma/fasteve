from fastapi import FastAPI, APIRouter
from .middleware.resource import ResourceMiddleware
from .endpoints import collections_endpoint_factory, home_endpoint
from .core import config
from .schema import BaseResponseSchema, BaseOutSchema, BaseSchema
from typing import List
from .resource import Resource
from .io.mongo import Mongo, MongoClient

class Fasteve(FastAPI):
    def __init__(self, resources: List[Resource] = [], data = Mongo) -> None:

        super().__init__()  # Instialise FastAPI super class

        # set defaults
        # validate user settings
        self.resources = resources
        self.config = self._validate_config(config)

        self._register_resource_middleware()

        self._register_home_endpoint()
        
        self.add_event_handler("startup", MongoClient.connect)  # this can't be in the application layer i.e. needs to come from data layer
        self.add_event_handler("shutdown", MongoClient.close)  # this can't be in the application layer i.e. needs to come from data layer
        
        self.data = data(self)  # eve pattern

        for resource in self.resources:
            self.register_resource(resource)

    def register_resource(self, resource: Resource) -> None:
        # process resource_settings
        # add name to api
        router = APIRouter()

        # add base out_schema 
        out_schema = type('Response', (resource.response_model, BaseOutSchema), {})

        class ResponseSchema(BaseResponseSchema):
            data: List[out_schema] 
        
        class PostResponseSchema(BaseSchema):
            data: List[out_schema] 

        for method in resource.resource_methods:
            if method == 'POST':
                router.add_api_route(
                    f"/{resource.name}", 
                    endpoint=collections_endpoint_factory(resource, method), 
                    response_model=PostResponseSchema, 
                    response_model_exclude_unset=True, 
                    methods=[method],
                ) 
            else: 
                router.add_api_route(
                    f"/{resource.name}", 
                    endpoint=collections_endpoint_factory(resource, method), 
                    response_model=ResponseSchema, 
                    response_model_exclude_unset=True, 
                    methods=[method],
                )
        self.include_router(
            router,
            tags=[resource.name],
        )
    def _register_home_endpoint(self) -> None:
        self.add_api_route(f"/", home_endpoint)

    def _register_resource_middleware(self) -> None:
        """Pass resources to every request"""
        # app is already passed to every request!
        # therfore I can use request.app.resources
        self.add_middleware(ResourceMiddleware, resources=self.resources)

    def _validate_config(self, config) -> None:
        return config
