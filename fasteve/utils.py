import hashlib
from json import dumps
from typing import List, NewType, Optional
from .resource import Resource
from dataclasses import dataclass
from pydantic import Field


def document_etag(value: dict, ignore_fields: List[str] = None) -> str:
    """ Computes and returns a valid ETag for the input value.
    """
    h = hashlib.sha1()
    h.update(dumps(value, sort_keys=True).encode("utf-8"))
    return h.hexdigest()


def Unique(tp: type) -> NewType:
    Unique = NewType("Fasteve_Unique", tp)
    return Unique


def DataRelation(resource, optional=True):
    # the optional flag is dumb. figure out a better way to do it.
    # basically i just want to use Option[] on the type
    #
    if optional:
        Relation = Field(None, data_relation=resource)
    else:
        Relation = Field(..., data_relation=resource)
    return Relation


@dataclass
class SubResource:
    resource: Resource
    id_field: str
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.resource.schema.name
