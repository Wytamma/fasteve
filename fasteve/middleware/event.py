from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp
from typing import Callable
from starlette.requests import Request
from ..resource import Resource
from typing import List

class EventMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, events: List) -> None:
        self.app = app
        self.dispatch_func = self.dispatch
        self.events = events

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.scope['path'] not in list_of_resource_urls:  # reverse
             # only run for resources:
            return await call_next(request)
        # pre events
        # look up event
        request = events['pre'][request.scope['path'][1:].split('/')[0]](request)
        res = await call_next(request)
        # post events
        res = events['post'][request.scope['path'][1:].split('/')[0]](res)
        return res
