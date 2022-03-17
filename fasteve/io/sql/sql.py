from fasteve.io.base import DataLayer
from fasteve.model import SQLModel
from fasteve.resource import Resource
from fasteve.core.utils import log
from typing import List, Tuple
from sqlmodel import Session, create_engine, select, delete


class SQLDataLayer(DataLayer):
    """
    SQLAlchemy data access layer for fasteve.
    """

    def init_app(self):
        connect_args = {"check_same_thread": False}
        self.engine = create_engine(
            self.app.config.SQL_URI, echo=True, connect_args=connect_args
        )

    def get_model(self, resource: Resource) -> SQLModel:
        return resource.model

    def connect(self) -> None:
        SQLModel.metadata.create_all(self.engine)

    def close(self) -> None:
        self.engine.dispose()

    async def find(
        self, resource: Resource, query: dict = {}, skip: int = 0, limit: int = 0
    ) -> Tuple[List[dict], int]:
        Model = self.get_model(resource)
        with Session(self.engine) as session:
            res = session.exec(select(Model)).all()
            return res, len(res)

    async def find_one(self, resource: Resource, query: dict) -> dict:
        """"""
        Model = self.get_model(resource)
        with Session(self.engine) as session:
            where = [getattr(Model, key) == value for key, value in query.items()]
            res = session.exec(select(Model).where(*where)).first()
            return res

    @log
    async def create(self, resource: Resource, payload: dict) -> dict:
        """"""
        Model = self.get_model(resource)
        model = Model(**payload)

        print("here", model)
        with Session(self.engine) as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            return model

    async def create_many(self, resource: Resource, payload: List[dict]) -> List[dict]:
        """"""
        Model = self.get_model(resource)
        models = [Model(**data) for data in payload]
        with Session(self.engine) as session:
            session.add_all(models)
            session.commit()
            for model in models:
                session.refresh(model)
        return models

    async def remove(self, resource: Resource) -> None:
        """Removes an entire set of documents from a
        database Model.
        """
        Model = self.get_model(resource)
        with Session(self.engine) as session:
            session.exec(delete(Model))
            session.commit()

    async def remove_item(self, resource: Resource, query: dict) -> None:
        """Removes a single document from a database collection."""
        Model = self.get_model(resource)
        with Session(self.engine) as session:
            where = [getattr(Model, key) == value for key, value in query.items()]
            model = session.exec(select(Model).where(*where)).first()
            session.delete(model)
            session.commit()

    async def replace_item(
        self, resource: Resource, query: dict, payload: dict
    ) -> None:
        """Replaces single document from a database collection"""
        Model = self.get_model(resource)
        with Session(self.engine) as session:
            where = [getattr(Model, key) == value for key, value in query.items()]
            model = session.exec(select(Model).where(*where)).first()
            for key, value in payload.items():
                setattr(model, key, value)
            session.add(model)
            session.commit()

    async def update_item(self, resource: Resource, query: dict, payload: dict) -> None:
        """Updates single document from a database collection"""
        Model = self.get_model(resource)
        with Session(self.engine) as session:
            where = [getattr(Model, key) == value for key, value in query.items()]
            model = session.exec(select(Model).where(*where)).first()
            for key, value in payload.items():
                setattr(model, key, value)
            session.add(model)
            session.commit()
