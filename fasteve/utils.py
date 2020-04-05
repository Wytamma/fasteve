import hashlib
from json import dumps
from typing import List


def document_etag(value: dict, ignore_fields: List[str] = None) -> str:
    """ Computes and returns a valid ETag for the input value.
    """
    h = hashlib.sha1()
    h.update(dumps(value, sort_keys=True).encode("utf-8"))
    return h.hexdigest()
