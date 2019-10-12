from starlette.requests import Request


def get(request: Request) -> dict:
    # needs database
    print(request.state.resources)
    return {}


def getitem() -> dict:
    return {}
