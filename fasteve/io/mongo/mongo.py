from fasteve.io.base import ConnectionException, DataLayer
from fastapi import HTTPException
from fasteve.resource import Resource
from pymongo.collection import Collection
from motor.motor_asyncio import AsyncIOMotorClient
from fasteve.core.utils import log
from typing import List, Tuple


class DataBase:
    client: AsyncIOMotorClient = None


db = DataBase()


class MongoClient:
    @classmethod
    def get_database(cls) -> AsyncIOMotorClient:
        return db.client

    @classmethod
    def connect(cls, MONGODB_URI: str, CONNECTION_TIMEOUT: int) -> None:
        try:
            client = AsyncIOMotorClient(
                str(MONGODB_URI),
                serverSelectionTimeoutMS=CONNECTION_TIMEOUT,
            )
        except Exception:
            raise ConnectionException
        db.client = client

    @classmethod
    def close(cls) -> None:
        db.client.close()


class MongoDataLayer(DataLayer):
    """MongoDB data access layer for Fasteve."""

    def __init__(self, app) -> None:  # type: ignore
        super().__init__(app)
        self.mongo_prefix = None

    # def init_app(self) -> None:
    #     print('*'*10, 'here')

    async def get_collection(self, resource: Resource) -> Collection:
        # maybe it would be better to use inject db with
        # Depends(get_database) at the path operation function?
        # By better I mean more FastAPI-ish.
        # However, then I have to pass the db all the way down to the
        # datalayer...
        try:
            client = MongoClient.get_database()
        except Exception as e:
            HTTPException(500, e)
        return client[self.app.config.MONGODB_NAME][resource.name]

    def connect(self) -> None:
        MongoClient.connect(
            self.app.config.MONGODB_URI, self.app.config.CONNECTION_TIMEOUT
        )

    def close(self) -> None:
        MongoClient.close()

    async def aggregate(
        self,
        resource: Resource,
        pipline: List[dict] = [],
        skip: int = 0,
        limit: int = 0,
    ) -> Tuple[List[dict], int]:
        collection = await self.get_collection(resource)

        paginated_results: List[dict] = []
        paginated_results.append({"$skip": skip})
        paginated_results.append({"$limit": limit})
        facet_pipelines: dict = {}
        facet_pipelines["paginated_results"] = paginated_results
        facet_pipelines["total_count"] = list({"$count": "count"})
        facet = {"$facet": facet_pipelines}
        pipline.append(facet)
        count = 0
        try:
            async for res in collection.aggregate(pipline):
                items = res["paginated_results"]
                if res["total_count"]:
                    # IndexError: list index out of range
                    count = res["total_count"][0]["count"]
        except Exception as e:
            raise e
        return items, count

    async def find(
        self, resource: Resource, query: dict = {}, skip: int = 0, limit: int = 0
    ) -> Tuple[List[dict], int]:
        """Retrieves a set of documents matching a given request. Queries can
        be expressed in two different formats: the mongo query syntax, and the
        python syntax. The first kind of query would look like: ::
            ?where={"name": "john doe"}
        while the second would look like: ::
            ?where=name=="john doe"
        :param resource: Resource object.
        """
        # process_query(q)
        collection = await self.get_collection(resource)
        items = []
        # Perform find and iterate results
        # https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#async-for
        try:
            async for row in collection.find(query, skip=skip, limit=limit):
                items.append(row)
        except Exception as e:
            raise e
        count = await collection.count_documents(query)
        return items, count

    async def find_one(self, resource: Resource, query: dict) -> dict:
        """"""
        collection = await self.get_collection(resource)
        try:
            item = await collection.find_one(query)
        except Exception as e:
            raise e
        return item

    @log
    async def create(self, resource: Resource, payload: dict) -> dict:
        """"""
        collection = await self.get_collection(resource)
        try:
            await collection.insert_one(payload)
        except Exception as e:
            raise e
        return payload

    async def create_many(self, resource: Resource, payload: List[dict]) -> List[dict]:
        """"""
        collection = await self.get_collection(resource)
        try:
            await collection.insert_many(payload)
        except Exception as e:
            raise e
        return payload

    async def remove(self, resource: Resource) -> None:
        """Removes an entire set of documents from a
        database collection.
        """
        collection = await self.get_collection(resource)
        try:
            await collection.delete_many({})
        except Exception as e:
            raise e

    async def remove_item(self, resource: Resource, query: dict) -> None:
        """Removes a single document from a database collection."""
        collection = await self.get_collection(resource)
        try:
            await collection.delete_one(query)
        except Exception as e:
            raise e

    async def replace_item(
        self, resource: Resource, query: dict, payload: dict
    ) -> None:
        """Replaces single document from a database collection"""
        collection = await self.get_collection(resource)
        try:
            await collection.replace_one(query, payload)
        except Exception as e:
            raise e

    async def update_item(self, resource: Resource, query: dict, payload: dict) -> None:
        """Updates single document from a database collection"""
        collection = await self.get_collection(resource)
        try:
            await collection.update_one(query, {"$set": payload})
        except Exception as e:
            raise e
