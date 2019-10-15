
from fasteve.io.base import DataLayer, ConnectionException, BaseJSONEncoder
from fasteve.core import config
from fasteve.core.utils import str_to_date
from fastapi import FastAPI
import asyncio
from fasteve.resource import Resource
from pymongo.collection import Collection
from fasteve.io.db import get_database

class MongoJSONEncoder(BaseJSONEncoder):
    """ Proprietary JSONEconder subclass used by the json render function.
    This is needed to address the encoding of special values.
    .. versionchanged:: 0.8.2
       Key-value pair order in DBRef are honored when encoding. Closes #1255.
    .. versionchanged:: 0.6.2
       Do not attempt to serialize callables. Closes #790.
    .. versionadded:: 0.2
    """

    def default(self, obj):
        if isinstance(obj, ObjectId):
            # BSON/Mongo ObjectId is rendered as a string
            return str(obj)
        if callable(obj):
            # when SCHEMA_ENDPOINT is active, 'coerce' rule is likely to
            # contain a lambda/callable which can't be jSON serialized
            # (and we probably don't want it to be exposed anyway). See #790.
            return "<callable>"
        if isinstance(obj, DBRef):
            retval = OrderedDict()
            retval["$ref"] = obj.collection
            retval["$id"] = str(obj.id)
            if obj.database:
                retval["$db"] = obj.database
            return json.RawJSON(json.dumps(retval))
        if isinstance(obj, decimal128.Decimal128):
            return str(obj)
        # delegate rendering to base class method
        return super(MongoJSONEncoder, self).default(obj)

class Mongo(DataLayer):
    """ MongoDB data access layer for Eve REST API.
    .. versionchanged:: 0.5
       Properly serialize nullable float and integers. #469.
       Return 400 if unsupported query operators are used. #387.
    .. versionchanged:: 0.4
       Don't serialize to objectid if value is null. #341.
    .. versionchanged:: 0.2
       Provide the specialized json serializer class as ``json_encoder_class``.
    .. versionchanged:: 0.1.1
       'serializers' added.
    """

    serializers = {
        "objectid": lambda value: ObjectId(value) if value else None,
        "datetime": str_to_date,
        "integer": lambda value: int(value) if value is not None else None,
        "float": lambda value: float(value) if value is not None else None,
        "number": lambda val: json.loads(val) if val is not None else None,
        "boolean": lambda v: {"1": True, "true": True, "0": False, "false": False}[
            str(v).lower()
        ],
        "dbref": lambda value: DBRef(
            value["$col"] if "$col" in value else value["$ref"],
            value["$id"],
            value["$db"] if "$db" in value else None,
        )
        if value is not None
        else None,
        "decimal": lambda value: decimal128.Decimal128(decimal.Decimal(str(value)))
        if value is not None
        else None,
    }

    # JSON serializer is a class attribute. Allows extensions to replace it
    # with their own implementation.
    json_encoder_class = MongoJSONEncoder

    operators = set(
        ["$gt", "$gte", "$in", "$lt", "$lte", "$ne", "$nin"]
        + ["$or", "$and", "$not", "$nor"]
        + ["$mod", "$regex", "$text", "$where"]
        + ["$options", "$search", "$language", "$caseSensitive"]
        + ["$diacriticSensitive", "$exists", "$type"]
        + ["$geoWithin", "$geoIntersects", "$near", "$nearSphere", "$centerSphere"]
        + ["$geometry", "$maxDistance", "$minDistance", "$box"]
        + ["$all", "$elemMatch", "$size"]
        + ["$bitsAllClear", "$bitsAllSet", "$bitsAnyClear", "$bitsAnySet"]
        + ["$center", "$expr"]
    )
    def init_app(self) -> None:
        self.mongo_prefix = None
    
    async def find(self, resource: Resource):
        """ Retrieves a set of documents matching a given request. Queries can
        be expressed in two different formats: the mongo query syntax, and the
        python syntax. The first kind of query would look like: ::
            ?where={"name": "john doe"}
        while the second would look like: ::
            ?where=name=="john doe"
        The resultset if paginated.
        :param resource: resource name.
        :param req: a :class:`ParsedRequest`instance.
        :param sub_resource_lookup: sub-resource lookup from the endpoint url.
        """
        collection = await self.get_collection(resource.route)
        items = []
        cursor = collection.find({})
        
        for row in await cursor.to_list(length=100):
            print('4')
            items.append(row)
        print(items)
        return items

    async def get_collection(self, collection_name: str) -> Collection:
        db = await get_database()
        return db[config.MONGO_DB][collection_name]

        