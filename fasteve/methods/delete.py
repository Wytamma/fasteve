from starlette.requests import Request
from fastapi import HTTPException


async def delete(request: Request) -> dict:
    try:
        item = await request.app.data.delete(request.state.resource)
    except Exception as e:
        raise e
    if not item:
        raise HTTPException(404)
    response = {}

    response["data"] = [item]
    return response
