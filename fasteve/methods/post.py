from starlette.requests import Request


async def post(request: Request) -> dict:

    payload = getattr(request, "payload")

    if len(payload) > 1:
        try:
            # TODO: bulk create config
            documents = await request.app.data.create_many(
                request.state.resource, payload
            )
        except Exception as e:
            raise e
    else:
        try:
            payload = payload[0]
            document = await request.app.data.create(request.state.resource, payload)
            documents = [document]
        except Exception as e:
            raise e

    response = {}

    response[request.app.config.DATA] = documents

    return response
