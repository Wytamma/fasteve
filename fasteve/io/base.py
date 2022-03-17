# -*- coding: utf-8 -*-

"""
    eve.io.base
    ~~~~~~~~~~~

    Standard interface implemented by Eve data layers.

    :copyright: (c) 2017 by Nicola Iarocci.
    :license: BSD, see LICENSE for more details.
"""
from typing import Optional, List, Tuple
from fasteve.resource import Resource


class ConnectionException(Exception):
    """Raised when DataLayer subclasses cannot find/activate to their
    database connection.

    :param driver_exception: the original exception raised by the source db
                             driver
    """

    def __init__(self, driver_exception: Optional[str] = None):
        self.driver_exception = driver_exception

    def __str__(self) -> str:
        msg = (
            "Error initializing the driver. Make sure the database server"
            "is running. "
        )
        if self.driver_exception:
            msg += "Driver exception: %s" % repr(self.driver_exception)
        return msg


class DataLayer:
    """Base data layer class. Defines the interface that actual data-access
    classes, being subclasses, must implement.

    Admittedly, this interface is a Mongo rip-off. See the io.mongo
    package for an implementation example.
    """

    class OriginalChangedError(Exception):
        pass

    # if custom serialize functions are needed, add them to the 'serializers'
    # dictionary, eg:
    # serializers = {'objectid': ObjectId, 'datetime': serialize_date}
    serializers: dict = {}

    def __init__(self, app) -> None:  # type: ignore
        """Implements extension pattern."""
        if app is not None:
            self.app = app
        else:
            self.app = None

    def init_app(self) -> None:
        """This is where you want to initialize the db driver so it will be
        alive through the whole instance lifespan.
        """
        raise NotImplementedError

    async def get_collection(self, resource: Resource) -> None:
        raise NotImplementedError

    def connect(self) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError

    async def find(self, resource: Resource, args: dict) -> Tuple[List[dict], int]:
        """Retrieves a set of documents (rows), matching the current request.
        Consumed when a request hits a collection/document endpoint
        (`/people/`).

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the db collection/table and base query (filter), if
                         any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). Be warned that `where` and `sort` expressions will
                    need proper parsing, according to the syntax that you want
                    to support with your driver. For example ``eve.io.Mongo``
                    supports both Python and Mongo-like query syntaxes.
        :param sub_resource_lookup: sub-resource lookup from the endpoint url.
        :param perform_count: wether a document count should be performed and
                              returned to the client.
        """
        raise NotImplementedError

    async def aggregate(
        self,
        resource: Resource,
        pipline: List[dict] = [],
        skip: int = 0,
        limit: int = 0,
    ) -> Tuple[List[dict], int]:
        """Perform an aggregation on the resource datasource and returns
        the result. Only implent this if the underlying db engine supports
        aggregation operations.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the db collection/table consumed by the resource.
        :param pipeline: aggregation pipeline to be executed.
        :param options: aggregation options to be considered.
        """
        raise NotImplementedError

    async def find_one(self, resource: Resource, lookup: dict) -> Optional[dict]:
        """Retrieves a single document/record. Consumed when a request hits an
        item endpoint (`/people/id/`).

        :param resource: resource being accessed. You should then use the
                         ``datasource`` helper function to retrieve both the
                         db collection/table and base query (filter), if any.
        :param req: an instance of ``eve.utils.ParsedRequest``. This contains
                    all the constraints that must be fulfilled in order to
                    satisfy the original request (where and sort parts, paging,
                    etc). As we are going to only look for one document here,
                    the only req attribute that you want to process here is
                    ``req.projection``.
        :param check_auth_value: a boolean flag indicating if the find
                                 operation should consider user-restricted
                                 resource access. Defaults to ``True``.
        :param force_auth_field_projection: a boolean flag indicating if the
                                            find operation should always
                                            include the user-restricted
                                            resource access field (if
                                            configured). Defaults to ``False``.

        :param **lookup: the lookup fields. This will most likely be a record
                         id or, if alternate lookup is supported by the API,
                         the corresponding query.
        """
        raise NotImplementedError

    def find_one_raw(self, resource: Resource, **lookup: dict) -> None:
        """Retrieves a single, raw document. No projections or datasource
        filters are being applied here. Just looking up the document using the
        same lookup.

        :param resource: resource name.
        :param ** lookup: lookup query.
        """
        raise NotImplementedError

    def find_list_of_ids(self, resource: Resource, ids: List) -> None:
        """Retrieves a list of documents based on a list of primary keys
        The primary key is the field defined in `ID_FIELD`.
        This is a separate function to allow us to use per-database
        optimizations for this type of query.

        :param resource: resource name.
        :param ids: a list of ids corresponding to the documents
        to retrieve
        :param client_projection: a specific projection to use
        :return: a list of documents matching the ids in `ids` from the
        collection specified in `resource`
        """
        raise NotImplementedError

    def create(self, resource: Resource, payload: dict) -> dict:
        """create a document into a resource collection/table.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the actual datasource name.
        :param doc_or_docs: json document or list of json documents to be added
                            to the database.
        """
        raise NotImplementedError

    async def create_many(self, resource: Resource, payload: List[dict]) -> List[dict]:
        """create a document into a resource collection/table.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve both
                         the actual datasource name.
        :param doc_or_docs: json document or list of json documents to be added
                            to the database.
        """
        raise NotImplementedError

    def update(
        self, resource: Resource, id_: str, updates: dict, original: dict
    ) -> None:
        """Updates a collection/table document/row.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.
        :param updates: json updates to be performed on the database document
                        (or row).
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        raise NotImplementedError

    def replace(
        self, resource: Resource, id_: str, document: dict, original: dict
    ) -> None:
        """Replaces a collection/table document/row.
        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param id_: the unique id of the document.
        :param document: the new json document
        :param original: definition of the json document that should be
        updated.
        :raise OriginalChangedError: raised if the database layer notices a
        change from the supplied `original` parameter.
        """
        raise NotImplementedError

    async def remove(self, resource: Resource) -> None:
        """Removes a document/row or an entire set of documents/rows from a
        database collection/table.

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        :param lookup: a dict with the query that documents must match in order
                       to qualify for deletion. For single document deletes,
                       this is usually the unique id of the document to be
                       removed.
        """
        raise NotImplementedError

    def combine_queries(self, query_a: dict, query_b: dict) -> None:
        """Takes two db queries and applies db-specific syntax to produce
        the intersection.
        """
        raise NotImplementedError

    def get_value_from_query(self, query: dict, field_name: str) -> None:
        """Parses the given potentially-complex query and returns the value
        being assigned to the field given in `field_name`.

        This mainly exists to deal with more complicated compound queries
        """
        raise NotImplementedError

    def query_contains_field(self, query: dict, field_name: str) -> None:
        """For the specified field name, does the query contain it?
        Used know whether we need to parse a compound query.
        """
        raise NotImplementedError

    def is_empty(self, resource: Resource) -> None:
        """Returns True if the collection is empty; False otherwise. While
        a user could rely on self.find() method to achieve the same result,
        this method can probably take advantage of specific datastore features
        to provide better performance.

        Don't forget, a 'resource' could have a pre-defined filter. If that is
        the case, it will have to be taken into consideration when performing
        the is_empty() check (see eve.io.mongo.mongo.py implementation).

        :param resource: resource being accessed. You should then use
                         the ``datasource`` helper function to retrieve
                         the actual datasource name.
        """
        raise NotImplementedError
