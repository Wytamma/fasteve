from starlette.config import Config

# Config will be read from environment variables and/or ".env" files.
config = Config(".env")

INFO = config("INFO", cast=str, default="_info")
API_VERSION = config("API_VERSION", cast=str, default="0.1")
HATEOAS = config("HATEOAS", cast=bool, default=True)
LINKS = config("LINKS", cast=str, default="_links")
MONGODB_URL = config("MONGODB_URL", cast=str, default="mongodb://localhost:27017")
MONGO_DB = config("MONGO_DB", cast=str, default="fasteve_db")
MAX_CONNECTIONS_COUNT  = config("MAX_CONNECTIONS_COUNT", cast=str, default="_links")
MIN_CONNECTIONS_COUNT  = config("MIN_CONNECTIONS_COUNT", cast=str, default="_links")

# default query parameters
QUERY_WHERE = config("QUERY_WHERE", cast=str, default="where")
QUERY_PROJECTION = config("QUERY_PROJECTION", cast=str, default="projection")
QUERY_SORT = config("QUERY_SORT", cast=str, default="sort")
QUERY_PAGE = config("QUERY_PAGE", cast=str, default="page")
QUERY_MAX_RESULTS = config("QUERY_MAX_RESULTS", cast=str, default="max_results")
QUERY_EMBEDDED = config("QUERY_EMBEDDED", cast=str, default="embedded")
QUERY_AGGREGATION = config("QUERY_AGGREGATION", cast=str, default="aggregate")
