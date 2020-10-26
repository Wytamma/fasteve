from inspect import iscoroutinefunction

class Events:
    def __init__(self, resources):
        self.METHODS = ["GET", "HEAD", "POST", "DELETE", "PUT", "PATCH"]
        
        # request events
        for method in self.METHODS:
            setattr(self, f"before_{method}", [])
            setattr(self, f"after_{method}", [])

        for resource in resources:
            for method in self.METHODS:
                setattr(self, f"before_{method}_{resource.name}", [])
                setattr(self, f"after_{method}_{resource.name}", [])

        
    async def run_before(self, request):
        for func in getattr(self, f"before_{request.method}"):
            if iscoroutinefunction(func):
                await func(request)
            else:
                func(request)
        for func in getattr(self, f"before_{request.method}_{request.state.resource.name}"):
            if iscoroutinefunction(func):
                await func(request)
            else:
                func(request)

    
    async def run_after(self, request, response):
        for func in getattr(self, f"after_{request.method}"):
            if iscoroutinefunction(func):
                await func(request, response)
            else:
                func(request, response)
        for func in getattr(self, f"after_{request.method}_{request.state.resource.name}"):
            if iscoroutinefunction(func):
                await func(request, response)
            else:
                func(request, response)




