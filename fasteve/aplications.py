from fastapi import FastAPI
from .middleware.setting import SettingsMiddleware
from .endpoints import collections_endpoint, home_endpoint


class Fasteve(FastAPI):
    def __init__(self, settings: dict = {"DOMAIN": {}}) -> None:

        super().__init__()  # Instialise FastAPI super class

        self.settings = settings
        self._register_settings_middleware()

        self._register_home_endpoint()
        
        domain = self.settings["DOMAIN"]

        for resource, resource_settings in domain.items():
            self.register_resource(resource, resource_settings)

    def register_resource(self, resource: str, resource_settings: dict) -> None:
        # process resource_settings

        # add route to api
        self.add_api_route(f"/{resource}", collections_endpoint)

    def _register_home_endpoint(self) -> None:
        self.add_api_route(f"/", home_endpoint)

    def _register_settings_middleware(self) -> None:
        """Pass validated settings to every request"""
        self._validate_settings()
        self.add_middleware(SettingsMiddleware, settings=self.settings)

    def _validate_settings(self):
        pass

