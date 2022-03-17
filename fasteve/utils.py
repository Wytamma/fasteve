import hashlib
from json import dumps
from typing import Any, List
from .resource import Resource
from pydantic import Field as MongoField


def document_etag(value: dict, ignore_fields: List[str] = None) -> str:
    """Computes and returns a valid ETag for the input value."""
    h = hashlib.sha1()
    h.update(dumps(value, sort_keys=True).encode("utf-8"))
    return h.hexdigest()


def Unique(old_type: Any) -> Any:
    Unique = type("Unique", (old_type,), {"__name__": "Unique"})
    return Unique


def DataRelation(resource: Resource, optional: bool = True) -> Any:
    # the optional flag is dumb. figure out a better way to do it.
    # basically i just want to use Option[] on the type
    #
    if optional:
        Relation = MongoField(None, data_relation=resource)
    else:
        Relation = MongoField(..., data_relation=resource)
    return Relation
