
from fasteve.io.base import DataLayer, ConnectionException, BaseJSONEncoder, Client
from fasteve.core import config
from fasteve.core.utils import str_to_date
from fastapi import FastAPI
import asyncio
from fasteve.resource import Resource
from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorClient
from fasteve.core.utils import log


class DataBase:
    client: AsyncIOMotorClient = None

db = DataBase()

class MongoClient(Client):
    async def get_database() -> AsyncIOMotorClient:
        return db.client

    def connect() -> None:
        print(config.MONGODB_URL)
        client = AsyncIOMotorClient(
            str(config.MONGODB_URL)
        )
        db.client = client

    def close():
        db.client.close()


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
        :param resource: Resource object.
        """
        # precess query 
        q = {}
        collection = await self.motor(resource)
        items = []
        # Perform find and iterate results
        # https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#async-for
        async for row in collection.find(q):
            items.append(row)
        return items
    
    @log
    async def insert(self, resource: Resource, payload):
        """ 
        """
        # precess query 
        payload = payload.dict()
        collection = await self.motor(resource)
        # https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#async-for
        try:
            result = await collection.insert_one(payload)
        except Exception as e:
            print(e)
        return [{'id': str(result.inserted_id), 'name': payload['name']}]

    async def motor(self, resource: str) -> Collection:
        # maybe it would be better to use inject db with 
        # Depends(get_database) at the path operation function?
        # By better I mean more FastAPI-ish. 
        # However, then I have to pass the db all the way down to the 
        # datalayer...
        db = await MongoClient.get_database()  
        return db[config.MONGO_DB][resource.route]

        