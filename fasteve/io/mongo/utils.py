def get_db_client():
    """
    Gets instance of MongoDB client for you to make DB queries.
    :return: MongoDBClient
    """
    from .mongo import Mongo

    client = Mongo()
    return client
