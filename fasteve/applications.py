from fastapi import FastAPI, APIRouter
from .middleware.resource import ResourceMiddleware
from .middleware.cors import CORSMiddleware
from .endpoints import (
    collections_endpoint_factory,
    home_endpoint,
    item_endpoint_factory,
    subresource_endpoint_factory,
)
from .events import Events
from .model import (
    BaseResponseModel,
    ItemBaseResponseModel,
    BaseModel,
    MongoModel,
    SQLModel,
)
from typing import List, Type, Optional, Union, Callable
from types import ModuleType
from .resource import Resource
from .io.mongo import MongoDataLayer
from .io.sql import SQLDataLayer
from .core.utils import log, MongoObjectId, is_new_type, repeat_every as repeat
from datetime import datetime
from pydantic import Field, create_model
import asyncio
import logging


class Fasteve(FastAPI):
    resources: List[Resource]
    cors_origins: List[str]
    data: Union[MongoDataLayer, SQLDataLayer]

    def __init__(
        self,
        resources: List[Resource] = [],
        data: Union[Type[MongoDataLayer], Type[SQLDataLayer]] = MongoDataLayer,
        cors_origins: List[str] = [],
    ) -> None:

        super().__init__()  # Initialise FastAPI super class

        # set defaults
        self.cors_origins = cors_origins

        # validate user settings
        self._validate_resources(resources)
        self.resources = resources

        from .core import config

        self._validate_config(config)
        self.config = config

        self._register_resource_middleware()
        self._register_CORS_middleware()
        self._register_home_endpoint()

        self.data = data(app=self)  # eve pattern

        if type(self.data) == Type[MongoDataLayer]:
            # TODO: move to datalayer
            for resource in self.resources:
                self.create_mongo_index(resource)

        for resource in self.resources:
            self.register_resource(resource)

        self.events = Events(resources)
        setattr(self.router, "add_event_handler", self.add_event_handler)
        self.add_event_handler("startup", self.data.connect)
        self.add_event_handler("shutdown", self.data.close)

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
        resource.model = self._embed_data_relation(resource.model)
        resource.model.__config__.extra = (  # type: ignore
            "forbid"  # type: ignore # TODO: this should be on the InModel
        )
        resource.response_model = self._embed_data_relation(
            resource.response_model, response=True
        )

        response_model = self._prepare_response_model(
            resource.response_model, resource.name
        )
        resource.response_model = response_model

        Response = create_model(
            f"ResponseModel_{resource.name}",
            data=(List[response_model], Field(..., alias=self.config.DATA)),  # type: ignore
            __base__=BaseResponseModel,
        )

        PostResponse = create_model(
            f"PostResponseModel_{resource.name}",
            data=(List[response_model], Field(..., alias=self.config.DATA)),  # type: ignore
            __base__=BaseModel,  # No meta or links
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
            f"ItemResponseModel_{resource.name}",
            data=(List[response_model], Field(..., alias=self.config.DATA)),  # type: ignore
            __base__=ItemBaseResponseModel,
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
                f"ResponseModel_{resource.name}_sub_resource_{sub_resource.name}",
                data=(List[sub_resource.resource.response_model], Field(..., alias=self.config.DATA)),  # type: ignore
                __base__=BaseResponseModel,
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
        collection = await self.data.get_collection(resource=resource)  # type: ignore
        # TODO: index should be removed at some point...
        # or at least check to see if there is one already
        res = await collection.create_index(field_name, unique=True)  # type: ignore # TODO: move to data layer
        print(f"Created unique index for {field_name} in {resource.name}")

    def create_mongo_index(self, resource: Resource) -> None:
        fields = resource.model.__fields__
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
        self, model: Union[MongoModel, SQLModel], response: bool = False
    ) -> Union[MongoModel, SQLModel]:

        fields = model.__fields__.keys()
        for name in fields:
            field = model.__fields__[name]

            if not "data_relation" in field.field_info.extra:
                continue

            data_relation = field.field_info.extra["data_relation"]
            outer_type_ = field.outer_type_
            many = False

            if outer_type_ not in (MongoObjectId, List[MongoObjectId]):
                raise ValueError(
                    f"Data relation ({model.__name__}: {name}) must be must be type MongoObjectId or List[MongoObjectId]"  # type: ignore
                )

            if response:
                response_model = self._prepare_response_model(
                    data_relation.response_model, data_relation.name + "_embedded"
                )  # add ids, create, updated, ect
                if outer_type_ == MongoObjectId:
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
        self, response_model: Union[MongoModel, SQLModel], name: str
    ) -> Union[MongoModel, SQLModel]:
        response_model.__config__.extra = "ignore"  # type: ignore
        return response_model

        create_model(
            f"out_model_{name}",
            id=(MongoObjectId, Field(..., alias="_id")),
            updated=(datetime, Field(..., alias="_updated")),
            created=(datetime, Field(..., alias="_created")),
            __base__=response_model,
        )

    def _register_home_endpoint(self) -> None:
        self.add_api_route(f"/", home_endpoint, methods=["GET"])

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
        elif self.config.CORS_ORIGINS:
            # global cors
            origins_raw = self.config.CORS_ORIGINS.split(",")
        # CORS
        origins = []
        # Set all CORS enabled origins
        if self.config.CORS_ORIGINS:
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
            print("Skipping validating:", resource)
