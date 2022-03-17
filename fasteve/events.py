from inspect import iscoroutinefunction


class Events:
    def __init__(self, resources: list) -> None:
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
        self.add("after", "read", levels=["resource", "item"])
        self.add("before", "create", ["items"])  # resource?
        self.add("after", "create", ["items"])  # resource?
        self.add("before", "replace", ["item"])
        self.add("after", "replace", ["item"])
        self.add("before", "update", ["item"])
        self.add("after", "update", ["item"])
        self.add("before", "delete", levels=["resource", "item"])
        self.add("after", "delete", levels=["resource", "item"])

    def add(self, timing: str, action: str, levels: list) -> None:
        assert timing in ("before", "after")

        for level in levels:
            setattr(self, f"{timing}_{action}_{level}", [])

        for resource in self.resources:
            for level in levels:
                setattr(self, f"{timing}_{action}_{level}_{resource.name}", [])

    async def run_callbacks(self, callbacks: list, *args: str) -> None:
        for func in callbacks:
            if iscoroutinefunction(func):
                await func(*args)
            else:
                func(*args)

    async def run(self, event: str, resource_name: str, *args: str) -> None:
        callbacks = getattr(self, event)
        await self.run_callbacks(callbacks, resource_name, *args)
        callbacks = getattr(self, f"{event}_{resource_name}")
        await self.run_callbacks(callbacks, *args)
