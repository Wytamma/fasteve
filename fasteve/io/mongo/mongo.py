from fasteve.io.base import Client, ConnectionException, DataLayer
from fasteve.core import config
from fastapi import HTTPException
from fasteve.resource import Resource
from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorClient
from fasteve.core.utils import log, ObjectID
from typing import Tuple, List


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


class MongoClient(Client):
    @classmethod
    async def get_database(cls) -> AsyncIOMotorClient:
        return db.client

    @classmethod
    def connect(cls) -> None:
        try:
            client = AsyncIOMotorClient(
                str(config.MONGODB_URI),
                serverSelectionTimeoutMS=config.CONNECTION_TIMEOUT,
            )
        except Exception:
            raise ConnectionException
        db.client = client

    @classmethod
    def close(cls) -> None:
        db.client.close()


class Mongo(DataLayer):
    """ MongoDB data access layer for Fasteve.
    """

    def init_app(self) -> None:
        self.mongo_prefix = None

    async def motor(self, resource: Resource) -> Collection:
        # maybe it would be better to use inject db with
        # Depends(get_database) at the path operation function?
        # By better I mean more FastAPI-ish.
        # However, then I have to pass the db all the way down to the
        # datalayer...
        try:
            client = await MongoClient.get_database()
        except Exception as e:
            HTTPException(500, e)
        return client[config.MONGODB_DATABASE][resource.name]

    async def aggregate(
        self,
        resource: Resource,
        pipline: List[dict] = [],
        skip: int = 0,
        limit: int = 0,
    ) -> Tuple[List[dict], int]:
        collection = await self.motor(resource)

        paginated_results = []
        paginated_results.append({"$skip": skip})
        paginated_results.append({"$limit": limit})
        facet_pipelines = {}
        facet_pipelines["paginated_results"] = paginated_results
        facet_pipelines["total_count"] = [{"$count": "count"}]
        facet = {"$facet": facet_pipelines}
        pipline.append(facet)
        count = 0
        try:
            async for res in collection.aggregate(pipline):
                print(res)
                items = res["paginated_results"]
                if res["total_count"]:
                    # IndexError: list index out of range
                    count = res["total_count"][0]["count"]
        except Exception as e:
            raise e
        return items, count

    async def find(
        self, resource: Resource, lookup: dict = {}, skip: int = 0, limit: int = 0
    ) -> Tuple[List[dict], int]:
        """ Retrieves a set of documents matching a given request. Queries can
        be expressed in two different formats: the mongo query syntax, and the
        python syntax. The first kind of query would look like: ::
            ?where={"name": "john doe"}
        while the second would look like: ::
            ?where=name=="john doe"
        :param resource: Resource object.
        """
        # process_query(q)
        collection = await self.motor(resource)
        items = []
        # Perform find and iterate results
        # https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#async-for
        try:
            async for row in collection.find(lookup, skip=skip, limit=limit):
                items.append(row)
        except Exception as e:
            raise e
        count = await collection.count_documents(lookup)
        return items, count

    async def find_one(self, resource: Resource, lookup: dict) -> dict:
        """ 
        """
        collection = await self.motor(resource)
        try:
            item = await collection.find_one(lookup)
        except Exception as e:
            raise e
        return item

    @log
    async def insert(self, resource: Resource, payload: dict) -> dict:
        """ 
        """
        collection = await self.motor(resource)
        try:
            await collection.insert_one(payload)
        except Exception as e:
            raise e
        return payload

    async def insert_many(self, resource: Resource, payload: List[dict]) -> List[dict]:
        """ 
        """
        collection = await self.motor(resource)
        try:
            await collection.insert_many(payload)
        except Exception as e:
            raise e
        return payload

    async def remove(self, resource: Resource) -> None:
        """ Removes an entire set of documents from a
        database collection.
        """
        collection = await self.motor(resource)
        try:
            await collection.delete_many({})
        except Exception as e:
            raise e

    async def remove_item(self, resource: Resource, item_id: ObjectID) -> None:
        """ Removes an entire set of documents from a
        database collection.
        """
        collection = await self.motor(resource)
        try:
            result = await collection.delete_one({"_id": item_id})
        except Exception as e:
            raise e
