import hashlib
from json import dumps
import asyncio
import logging
from asyncio import ensure_future
from functools import wraps
from traceback import format_exception
from typing import Any, Callable, Coroutine, Optional, Union, List, NewType

from starlette.concurrency import run_in_threadpool

def document_etag(value: dict, ignore_fields: List[str] = None) -> str:
    """ Computes and returns a valid ETag for the input value.
    """
    h = hashlib.sha1()
    h.update(dumps(value, sort_keys=True).encode("utf-8"))
    return h.hexdigest()

def Unique(tp: type) -> type:
  Unique = NewType('Fasteve_Unique', tp)
  return Unique

def DataRelation():
    pass

def SubResource():
    pass