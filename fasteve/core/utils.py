from functools import wraps
from bson import ObjectId
from typing import Callable, Any, Generator, Type, NewType


def log(func: Callable) -> Callable:
    """
    A decorator that wraps the passed in function and logs 
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Callable:
        ", ".join([str(arg) for arg in args])
        keywords = ", ".join([f"{k}={str(v)}" for k, v in kwargs.items()])
        # print(f"LOG: {func.__name__}({arugemnts}, {keywords})")
        return func(*args, **kwargs)

    return wrapper


class ObjectID(str):
    @classmethod
    def __get_validators__(cls) -> Generator:
        yield cls.validate

    @classmethod
    def validate(cls, v: ObjectId) -> ObjectId:
        if not ObjectId.is_valid(str(v)):
            raise ValueError(f"Not a valid ObjectId: {v}")
        return ObjectId(str(v))

test_type = NewType('test_type', str)

def is_new_type(type_: Type[Any]) -> bool:
    """
    Check whether type_ was created using typing.NewType
    """
    return isinstance(type_, test_type.__class__) and hasattr(type_, '__supertype__')  # type: ignore