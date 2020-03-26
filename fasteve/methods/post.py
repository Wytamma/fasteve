from starlette.requests import Request
from datetime import datetime
from fasteve.core.utils import log
from fasteve.core import config

@log
async def post(request: Request) -> dict:
    # TODO: bulk insert
    
    payload = request.payload
    payload['created'] = datetime.now()
    payload['updated'] = datetime.now()
    
    try:
        documents = await request.app.data.insert(request.state.resource, payload)
    except Exception as e:
        print(e)

    response = {}
    
    response['data'] = documents
    
    return response


def getitem() -> dict:
    return {}
