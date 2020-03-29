from fasteve.io.base import BaseJSONEncoder, Client, DataLayer
from fasteve.core import config
from fasteve.core.utils import str_to_date
from fastapi import HTTPException
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
        try:
            client = AsyncIOMotorClient(str(config.MONGODB_URI))
            # check that the client is connected
            client.server_info()
        except:
            raise HTTPException(500)
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

    async def find(self, resource: Resource, args: dict):
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
        try:
            async for row in collection.find(q, skip=args["skip"], limit=args["limit"]):
                # row['id'] = row['_id']
                items.append(row)
        except Exception as e:
            raise e
        count = await collection.count_documents(q)
        return items, count

    async def find_one(self, resource: Resource, item_id):
        """ 
        """
        collection = await self.motor(resource)
        try:
            item = await collection.find_one({"_id": item_id})
        except Exception as e:
            raise e
        return item

    @log
    async def insert(self, resource: Resource, payload):
        """ 
        """
        # precess query
        collection = await self.motor(resource)
        # https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#async-for
        try:
            result = await collection.insert_one(payload)
        except Exception as e:
            raise e
        payload["id"] = result.inserted_id
        return [payload]

    async def insert_many(self, resource: Resource, payload):
        """ 
        """
        # precess query
        collection = await self.motor(resource)
        # https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#async-for
        try:
            await collection.insert_many(payload)
        except Exception as e:
            raise e
        # for (item, id) in zip(payload, result.inserted_ids):
        #    item.update({'id':id})
        print(payload)
        return payload

    async def motor(self, resource: str) -> Collection:
        # maybe it would be better to use inject db with
        # Depends(get_database) at the path operation function?
        # By better I mean more FastAPI-ish.
        # However, then I have to pass the db all the way down to the
        # datalayer...
        try:
            db = await MongoClient.get_database()
        except Exception as e:
            HTTPException(500, e)
        return db[config.MONGODB_DATABASE][resource.name]


def _convert_sort_request_to_dict(self, re):
    """ Converts the contents of a `ParsedRequest`'s `sort` property to
    a dict
    """
    client_sort = {}
    if req and req.sort:
        try:
            # assume it's mongo syntax (ie. ?sort=[("name", 1)])
            client_sort = ast.literal_eval(req.sort)
        except ValueError:
            # it's not mongo so let's see if it's a comma delimited string
            # instead (ie. "?sort=-age, name").
            sort = []
            for sort_arg in [s.strip() for s in req.sort.split(",")]:
                if sort_arg[0] == "-":
                    sort.append((sort_arg[1:], -1))
                else:
                    sort.append((sort_arg, 1))
            if len(sort) > 0:
                client_sort = sort
        except Exception as e:
            self.app.logger.exception(e)
            abort(400, description=debug_error_message(str(e)))
    return client_sort


def _convert_where_request_to_dict(self, req):
    """ Converts the contents of a `ParsedRequest`'s `where` property to
    a dict
    """
    query = {}
    if req and req.where:
        try:
            query = self._sanitize(json.loads(req.where))
        except HTTPException:
            # _sanitize() is raising an HTTP exception; let it fire.
            raise
        except:
            # couldn't parse as mongo query; give the python parser a shot.
            try:
                query = parse(req.where)
            except ParseError:
                abort(
                    400,
                    description=debug_error_message("Unable to parse `where` clause"),
                )
    return query
