from fastapi import FastAPI, APIRouter
from .middleware.resource import ResourceMiddleware
from .middleware.cors import CORSMiddleware
from .endpoints import (
    collections_endpoint_factory,
    home_endpoint,
    item_endpoint_factory,
    subresource_endpoint_factory,
)
from .core import config
from .events import Events
from .schema import BaseResponseSchema, BaseSchema, ItemBaseResponseSchema
from typing import List, Type, Optional, Union, Callable
from types import ModuleType
from .resource import Resource
from .io.mongo import Mongo, MongoClient
from .io.base import DataLayer
from .core.utils import log, ObjectID, is_new_type, repeat_every as repeat
from datetime import datetime
from pydantic import Field, create_model, BaseModel
import asyncio
import logging


class Fasteve(FastAPI):
    def __init__(
        self,
        resources: List[Resource] = [],
        data: Type[DataLayer] = Mongo,
        cors_origins: List[str] = [],
    ) -> None:

        super().__init__()  # Initialise FastAPI super class

        # set defaults
        self.cors_origins = cors_origins

        # validate user settings
        self._validate_resources(resources)
        self.resources = resources

        self._validate_config(config)
        self.config = config

        self._register_resource_middleware()
        self._register_CORS_middleware()
        self._register_home_endpoint()

        # connect to db
        MongoClient.connect()

        self.data = data(app=self)  # eve pattern

        for resource in self.resources:
            self.create_mongo_index(resource)

        for resource in self.resources:
            self.register_resource(resource)

        self.events = Events(resources)
        setattr(self.router, "add_event_handler", self.add_event_handler)
        self.add_event_handler(
            "shutdown", MongoClient.close
        )  # this can't be in the application layer i.e. needs to come from data layer

    def add_event_handler(self, event_type: str, func: Callable) -> None:
        if event_type == "startup":
            self.router.on_startup.append(func)
        elif event_type == "shutdown":
            self.router.on_shutdown.append(func)
        else:
            # Event Hooks
            try:
                getattr(self.events, event_type).append(func)
            except Exception as e:
                raise e

    @log
    def register_resource(self, resource: Resource) -> None:
        print(f"Registering Resource: {resource.name}")
        # process resource_settings
        # add name to api
        router = APIRouter()

        # check models for data relations
        resource.schema = self._embed_data_relation(resource.schema)
        resource.schema.__config__.extra = (  # type: ignore
            "forbid"  # type: ignore # TODO: this should be on the InSchema
        )
        resource.response_model = self._embed_data_relation(
            resource.response_model, response=True
        )

        response_model = self._prepare_response_model(
            resource.response_model, resource.name
        )

        Response = create_model(
            f"ResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=BaseResponseSchema,
        )

        PostResponse = create_model(
            f"PostResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=BaseSchema,  # No meta or links
        )

        for method in resource.resource_methods:
            if method == "POST":
                router.add_api_route(
                    f"/{resource.name}",
                    endpoint=collections_endpoint_factory(resource, method),
                    response_model=PostResponse,
                    response_model_exclude_unset=True,
                    methods=[method],
                    status_code=201,
                )
            elif method == "DELETE":
                router.add_api_route(
                    f"/{resource.name}",
                    endpoint=collections_endpoint_factory(resource, method),
                    methods=[method],
                    status_code=204,
                )
            else:
                router.add_api_route(
                    f"/{resource.name}",
                    endpoint=collections_endpoint_factory(resource, method),
                    response_model=Response,
                    response_model_exclude_unset=True,
                    methods=[method],
                )

        ItemResponse = create_model(
            f"ItemResponseSchema_{resource.name}",
            data=(List[response_model], Field(..., alias="_data")),  # type: ignore
            __base__=ItemBaseResponseSchema,
        )

        for method in resource.item_methods:
            if method in ["PUT", "DELETE", "PATCH"]:
                router.add_api_route(
                    f"/{resource.name}/{{{str(resource.item_name) + '_id'}}}",
                    endpoint=item_endpoint_factory(resource, method),
                    methods=[method],
                    status_code=204,
                )
            else:
                router.add_api_route(
                    f"/{resource.name}/{{{str(resource.item_name) + '_id'}}}",
                    endpoint=item_endpoint_factory(resource, method),
                    response_model=ItemResponse,
                    response_model_exclude_unset=True,
                    methods=[method],
                )

        for sub_resource in resource.sub_resources:
            Response = create_model(
                f"ResponseSchema_{resource.name}_sub_resource_{sub_resource.name}",
                data=(List[sub_resource.resource.response_model], Field(..., alias="_data")),  # type: ignore
                __base__=BaseResponseSchema,
            )

            print(f"Registering Sub Resource: {sub_resource.name}")
            router.add_api_route(
                f"/{resource.name}/{{{str(resource.item_name) + '_id'}}}/{sub_resource.name}",
                endpoint=subresource_endpoint_factory(resource, "GET", sub_resource),
                response_model=Response,
                response_model_exclude_unset=True,
                methods=["GET"],
            )

        # TODO: api versioning
        self.include_router(
            router,
            tags=[str(resource.name)],
        )

    async def _create_mongo_index_internal(
        self, resource: Resource, field_name: str
    ) -> None:
        collection = await self.data.get_collection(resource)
        # TODO: index should be removed at some point...
        # or at least check to see if there is one already
        res = await collection.create_index(field_name, unique=True)  # type: ignore # TODO: move to data layer
        print(f"Created unique index for {field_name} in {resource.name}")

    def create_mongo_index(self, resource: Resource) -> None:
        fields = resource.schema.__fields__
        for name in fields:
            field = fields[name]
            type_ = field.type_
            if not is_new_type(type_):
                continue
            if type_.__name__ == "Unique":
                asyncio.create_task(self._create_mongo_index_internal(resource, name))

    def repeat_every(
        self,
        *,
        seconds: float,
        wait_first: bool = False,
        logger: Optional[logging.Logger] = None,
        raise_exceptions: bool = False,
        max_repetitions: Optional[int] = None,
    ) -> Callable:
        """https://stackoverflow.com/a/52518284/5209891"""
        dec2 = repeat(
            seconds=seconds,
            wait_first=wait_first,
            logger=logger,
            raise_exceptions=raise_exceptions,
            max_repetitions=max_repetitions,
        )
        dec1 = self.on_event("startup")

        def merged_decorator(func: Callable) -> Callable:
            return dec1(dec2(func))

        return merged_decorator

    def _embed_data_relation(
        self, model: Type[BaseModel], response: bool = False
    ) -> Type[BaseModel]:

        fields = model.__fields__.keys()
        for name in fields:
            field = model.__fields__[name]

            if not "data_relation" in field.field_info.extra:
                continue

            data_relation = field.field_info.extra["data_relation"]
            outer_type_ = field.outer_type_
            many = False

            if outer_type_ not in (ObjectID, List[ObjectID]):
                raise ValueError(
                    f"Data relation ({model.__name__}: {name}) must be must be type ObjectID or List[ObjectID]"
                )

            if response:
                response_model = self._prepare_response_model(
                    data_relation.response_model, data_relation.name + "_embedded"
                )  # add ids, create, updated, ect
                if outer_type_ == ObjectID:
                    type_ = Union[Type[outer_type_], Type[response_model]]  # type: ignore # meta typing
                else:
                    type_ = Union[Type[outer_type_], List[Type[response_model]]]  # type: ignore # meta typing
                    many = True
            else:
                type_ = outer_type_  # type: ignore # meta typing

            if field.required:
                relation_field = {
                    name: (type_, Field(..., data_relation=data_relation, many=many))
                }
            else:
                relation_field = {
                    name: (type_, Field(None, data_relation=data_relation, many=many))
                }

            # relation_field = {name:(type_,field)}
            model = create_model(model.__name__, **relation_field, __base__=model)  # type: ignore # TODO: define multi-type
        return model

    def _prepare_response_model(
        self, response_model: Type[BaseModel], name: str
    ) -> Type[BaseModel]:
        return create_model(
            f"out_schema_{name}",
            id=(ObjectID, Field(..., alias="_id")),
            updated=(datetime, Field(..., alias="_updated")),
            created=(datetime, Field(..., alias="_created")),
            __base__=response_model,
        )

    def _register_home_endpoint(self) -> None:
        self.add_api_route(f"/", home_endpoint)

    def _register_resource_middleware(self) -> None:
        """Pass resources to every request"""
        # app is already passed to every request!
        # therfore I can use request.app.resources
        self.add_middleware(ResourceMiddleware, resources=self.resources)

    def _register_CORS_middleware(self) -> None:
        """Set global Cross-Origin Resource Sharing"""
        if self.cors_origins:
            # app level cors
            origins_raw = self.cors_origins
        elif config.CORS_ORIGINS:
            # global cors
            origins_raw = config.CORS_ORIGINS.split(",")
        # CORS
        origins = []
        # Set all CORS enabled origins
        if config.CORS_ORIGINS:
            for origin in origins_raw:
                use_origin = origin.strip()
                origins.append(use_origin)
            self.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

    def _validate_config(self, config: ModuleType) -> None:
        # raise errors if config is invalid
        pass

    def _validate_resources(self, resources: List[Resource]) -> None:
        # raise errors if resource is invalid
        for resource in resources:
            # check methods i.e. post only on resource
            # check alt_id is unique
            pass
