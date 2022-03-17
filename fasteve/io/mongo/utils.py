def render_pymongo_error(details: dict) -> dict:
    key = list(details["keyValue"].keys())[0]
    val = details["keyValue"][key]
    msg = {
        "loc": ["body", "model", key],
        "msg": f"value '{val}' is not unique",
        "type": "value_error.not_unique",
    }
    return msg
