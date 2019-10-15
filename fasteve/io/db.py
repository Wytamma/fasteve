# need to override
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from fasteve.core import config, utils

from motor.motor_asyncio import AsyncIOMotorClient


class DataBase:
    client: AsyncIOMotorClient = None

db = DataBase()

async def get_database() -> AsyncIOMotorClient:
    return db.client

@utils.log
def connect() -> None:
    print(config.MONGODB_URL)
    client = AsyncIOMotorClient(
        str(config.MONGODB_URL)
    )
    db.client = client

def close():
    db.client.close()

