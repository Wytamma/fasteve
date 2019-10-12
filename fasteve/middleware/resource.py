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
        request.state.resources = self.resources
        return await call_next(request)
