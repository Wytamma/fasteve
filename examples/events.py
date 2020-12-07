from fasteve import Fasteve, BaseSchema, Resource, ObjectID, SubResource, Response
from fasteve.utils import Unique, DataRelation
from typing import Optional, List, NewType, Union, Any
from pydantic import EmailStr, SecretStr, Field, BaseModel
from datetime import datetime
from time import sleep
from starlette.requests import Request


class UserIn(BaseSchema):
    username: str
    password: str
    email: EmailStr
    full_name: Optional[str] = None


class UserOut(BaseSchema):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


users = Resource(
    schema=UserIn,
    name='users',
    resource_methods=["GET", "POST", "DELETE", "HEAD"],
    response_model=UserOut,
    item_methods=["GET", "DELETE", "PUT", "PATCH"],
    bulk_inserts=False,
)

resources = [users]

app = Fasteve(resources=resources, cors_origins=["*"])

@app.on_event("before_GET_users")
async def before_GET_users_callback(request: Request):
    print(f"LOG: {request.url}")

@app.on_event("after_fetch_resource_users")
async def after_fetch_resource_callback(response: dict):
    print(response) 

def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password

class UserInDB(BaseSchema):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: Optional[str] = None

def user_in_db_rep(user_in):
    hashed_password = fake_password_hasher(user_in['password'])
    user_in_db = UserInDB(**user_in, hashed_password=hashed_password)
    return user_in_db.dict()

@app.on_event("before_insert_items_users")
async def before_insert_callback(items: List[dict]):
    for item in items:
        user_in_db_dict = user_in_db_rep(item)
        item.clear()
        item.update(user_in_db_dict)

@app.on_event("after_insert_items_users")
async def before_insert_callback(response: dict):
    print(response)

@app.on_event("before_replace_item_users")
async def before_insert_callback(items: List[dict]):
    for item in items:
        user_in_db_dict = user_in_db_rep(item)
        item.clear()
        item.update(user_in_db_dict)

@app.on_event("after_replace_item_users")
async def before_insert_callback(response: dict):
    print(response)




