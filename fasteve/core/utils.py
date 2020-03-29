from functools import wraps
from bson import ObjectId

def log(func):
    """
    A decorator that wraps the passed in function and logs 
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        arugemnts = ', '.join([str(arg) for arg in args])
        keywords = ', '.join([f'{k}={str(v)}' for k,v in kwargs.items()])
        #print(f"LOG: {func.__name__}({arugemnts}, {keywords})")
        return func(*args, **kwargs)
    return wrapper


def str_to_date(string):
    """ Converts a date string formatted as defined in the configuration
        to the corresponding datetime value.
    :param string: the RFC-1123 string to convert to datetime value.
    """
    return datetime.strptime(string, config.DATE_FORMAT) if string else None

def parse_request(request):
    pass

class ObjectID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            return ValueError(f"Not a valid ObjectId: {v}")
        return ObjectId(str(v))