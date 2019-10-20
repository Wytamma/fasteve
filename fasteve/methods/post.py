from starlette.requests import Request
from datetime import datetime
from fasteve.core.utils import log

@log
async def post(request: Request) -> dict:
    
    payload = request.payload
    payload['created'] = datetime.now()
    payload['updated'] = datetime.now()
    
    try:
        res = await request.app.data.insert(request.state.resource, payload)
        return {'data': res}
    except Exception as e:
        print(e)



def getitem() -> dict:
    return {}
