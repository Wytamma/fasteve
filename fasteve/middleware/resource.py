from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
from typing import Callable
from starlette.requests import Request
from ..resource import Resource


class ResourceMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, resources: Resource) -> None:
        self.app = app
        self.dispatch_func = self.dispatch
        self.resources = resources

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        resource = None
        if request.scope['path'] != '/':
            # Use pattern matching to find resource
            route = request.scope['path'][1:].split('/')[0]
            resource = next((resource for resource in self.resources if resource.name == route), None)
        request.state.resource = resource
        return await call_next(request)
