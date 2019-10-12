from fastapi import FastAPI
from .middleware.resource import ResourceMiddleware
from .endpoints import collections_endpoint, home_endpoint
from .core import config as default_config
from typing import List
from .resource import Resource


class Fasteve(FastAPI):
    def __init__(self, resources: List[Resource] = []) -> None:

        super().__init__()  # Instialise FastAPI super class

        # set setting defualts
        # load user settings
        # validate user settings
        self.resources = resources
        self.config = default_config

        self._validate_settings()
        self._register_resource_middleware()

        self._register_home_endpoint()

        for resource in self.resources:
            self.register_resource(resource)

    def register_resource(self, resource: Resource) -> None:
        # process resource_settings
        # add route to api

        # should i be smarter about how these are registered?
        # fastapi already as get, post, put, etc methods
        # I don't think i can use this methods as they are really
        # a human api. i can just go down one layer (still in fastapi)
        # and use add_api_route then have a swtich in collections.
        # pre and post request processing can be handeled by middlewear.
        self.add_api_route(f"/{resource.route}", collections_endpoint)

    def _register_home_endpoint(self) -> None:
        self.add_api_route(f"/", home_endpoint)

    def _register_resource_middleware(self) -> None:
        """Pass resources to every request"""
        # app is already passed to every request!
        # therfore I can use request.app.resources
        self.add_middleware(ResourceMiddleware, resources=self.resources)

    def _validate_settings(self) -> None:
        pass
