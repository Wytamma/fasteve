from starlette.requests import Request

from fasteve.core.utils import log

@log
async def post(request: Request) -> dict:
    print('ere')
    try:
        res = await request.app.data.insert(request.state.resource, request.payload)
        return {'data': res}
    except Exception as e:
        print(e)



def getitem() -> dict:
    return {}
