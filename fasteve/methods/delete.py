from starlette.requests import Request
from fasteve.core.utils import ObjectID


async def delete(request: Request) -> None:
    try:
        await request.app.data.remove(request.state.resource)
    except Exception as e:
        raise e


async def delete_item(request: Request, item_id: ObjectID) -> None:
    try:
        await request.app.data.remove_item(request.state.resource, item_id)
    except Exception as e:
        raise e
