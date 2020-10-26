from inspect import iscoroutinefunction
from typing import List


class Events:
    def __init__(self, resources):
        self.METHODS = ["GET", "HEAD", "POST", "DELETE", "PUT", "PATCH"]
        self.resources = resources
        
        # request events
        for method in self.METHODS:
            setattr(self, f"before_{method}", [])
            setattr(self, f"after_{method}", [])

        for resource in self.resources:
            for method in self.METHODS:
                setattr(self, f"before_{method}_{resource.name}", [])
                setattr(self, f"after_{method}_{resource.name}", [])

        # db events 
        self.add('after', 'fetch')
        self.add('before', 'insert', ['items'])
        self.add('after', 'insert', ['items'])
        self.add('before', 'replace', ['item'])
        self.add('after', 'replace', ['item'])
        self.add('before', 'update', ['item'])
        self.add('after', 'update', ['item'])
        self.add('before', 'delete')
        self.add('after', 'delete')

    def add(self, timing, action:str, levels=["resource", "item"]):
        assert timing in ('before', 'after')

        for level in levels:
            setattr(self, f"{timing}_{action}_{level}", [])

        for resource in self.resources:
            for level in levels:
                setattr(self, f"{timing}_{action}_{level}_{resource.name}", [])
        
    async def run_callbacks(self, callbacks, *args):
        for func in callbacks:
            if iscoroutinefunction(func):
                await func(*args)
            else:
                func(*args)

    async def run(self, event, resource_name, *args):
        callbacks = getattr(self, event)
        await self.run_callbacks(callbacks, resource_name, *args)
        callbacks = getattr(self, f"{event}_{resource_name}")
        await self.run_callbacks(callbacks, *args)

    async def run_before_request(self, request):
        callbacks = getattr(self, f"before_{request.method}")
        await self.run_callbacks(callbacks, request)
        callbacks = getattr(self, f"before_{request.method}_{request.state.resource.name}")
        await self.run_callbacks(callbacks, request)
    
    async def run_after_request(self, request, response):
        callbacks = getattr(self, f"after_{request.method}")
        await self.run_callbacks(callbacks, request, response)
        callbacks = getattr(self, f"after_{request.method}_{request.state.resource.name}")
        await self.run_callbacks(callbacks, request, response)

