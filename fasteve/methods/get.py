from starlette.requests import Request
from fasteve.io.mongo import Mongo
from fasteve.core.utils import log


async def get(request: Request) -> dict:
    res = await request.app.data.find(request.state.resource)
    return {'data':res}


def getitem() -> dict:
    return {}
