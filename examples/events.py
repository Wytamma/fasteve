from fasteve import Fasteve, MongoModel, Resource, MongoObjectId, SubResource, Response
from fasteve.utils import Unique, DataRelation
from typing import Optional, List, NewType, Union, Any
from pydantic import EmailStr, SecretStr, Field, MongoModel
from datetime import datetime
from time import sleep
from starlette.requests import Request


class UserIn(MongoModel):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None


class UserOut(MongoModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


users = Resource(
    model=UserIn,
    name="users",
    resource_methods=["GET", "POST", "DELETE", "HEAD"],
    response_model=UserOut,
    item_methods=["GET", "DELETE", "PUT", "PATCH"],
    bulk_create=False,
)

resources = [users]

app = Fasteve(resources=resources, cors_origins=["*"])


@app.on_event("before_GET_users")
async def before_GET_users_callback(request: Request):
    print(f"LOG: {request.url}")


@app.on_event("after_read_resource_users")
async def after_read_resource_callback(response: dict):
    print(response)


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


class UserInDB(MongoModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: Optional[str] = None


def user_in_db_rep(user_in):
    hashed_password = fake_password_hasher(user_in["password"])
    user_in_db = UserInDB(**user_in, hashed_password=hashed_password)
    return user_in_db.dict()


@app.on_event("before_create_items_users")
async def before_create_callback(items: List[dict]):
    for item in items:
        user_in_db_dict = user_in_db_rep(item)
        item.clear()
        item.update(user_in_db_dict)


@app.on_event("after_create_items_users")
async def before_create_callback(response: dict):
    print(response)


@app.on_event("before_replace_item_users")
async def before_create_callback(items: List[dict]):
    for item in items:
        user_in_db_dict = user_in_db_rep(item)
        item.clear()
        item.update(user_in_db_dict)


@app.on_event("after_replace_item_users")
async def before_create_callback(response: dict):
    print(response)
