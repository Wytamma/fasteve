from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class SettingsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, settings: dict = None) -> None:
        self.app = app
        self.dispatch_func = self.dispatch
        self.settings = settings
        
    async def dispatch(self, request, call_next):
        request.state.settings = self.settings
        return await call_next(request)