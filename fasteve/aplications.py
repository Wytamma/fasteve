from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Type, Union
import uvicorn
from fastapi import FastAPI

from .endpoints import collections_endpoint


class Fasteve(FastAPI):

    def __init__(
        self,
        settings: str = "settings.py",
    ) -> None:

        super().__init__()  # Instialise FastAPI super class
        
        self.settings = settings
        
        # settings validation to config?

        domain = self.settings['DOMAIN']

        for resource, settings in domain.items():
            self.register_resource(resource, settings)


    def register_resource(self, resource: str, settings: dict) -> None:
        # process settings

        # add route to api
        self.add_api_route(f"/{resource}", collections_endpoint)
