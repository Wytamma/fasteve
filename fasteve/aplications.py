from fastapi import FastAPI, APInamer
from .middleware.resource import ResourceMiddleware
from .endpoints import collections_endpoint_factory, home_endpoint
from .core import config
from .schema import BaseResponseSchema
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
        
        self.add_event_handler("startup", MongoClient.connect)
        self.add_event_handler("shutdown", MongoClient.close)
        
        self.data = data(self)  #eve pattern

        for resource in self.resources:
            self.register_resource(resource)

    def register_resource(self, resource: Resource) -> None:
        # process resource_settings
        # add name to api
        namer = APInamer()

        class ResponseSchema(BaseResponseSchema):
            data: List[resource.response_model] # remove unwanted values from the schema 

        for method in resource.resource_methods:
            namer.add_api_name(
                f"/{resource.name}", 
                endpoint=collections_endpoint_factory(resource, method), 
                response_model=ResponseSchema, 
                response_model_skip_defaults=True, 
                methods=[method]
            )
        self.include_namer(
            namer,
            tags=[resource.name],
        )
    def _register_home_endpoint(self) -> None:
        self.add_api_name(f"/", home_endpoint)

    def _register_resource_middleware(self) -> None:
        """Pass resources to every request"""
        # app is already passed to every request!
        # therfore I can use request.app.resources
        self.add_middleware(ResourceMiddleware, resources=self.resources)

    def _validate_config(self, config) -> None:
        return config
