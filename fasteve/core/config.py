from starlette.config import Config as starletteConfig

# Config will be read from environment variables and/or ".env" files.
# Should envirmonet variables have priority?


config = starletteConfig(".env")
INFO = config("FASTEVE_INFO", cast=str, default="_info")
API_VERSION = config("FASTEVE_API_VERSION", cast=str, default="0.1")
HATEOAS = config("FASTEVE_HATEOAS", cast=bool, default=True)
LINKS = config("FASTEVE_LINKS", cast=str, default="_links")
META = config("FASTEVE_META", cast=str, default="_meta")
DATA = config("FASTEVE_DATA", cast=str, default="_data")
PAGINATION = config("FASTEVE_PAGINATION", cast=bool, default=True)
MONGODB_URI = config(
    "FASTEVE_MONGODB_URI", cast=str, default="mongodb://localhost:27017"
)
MONGODB_NAME = config("FASTEVE_MONGODB_NAME", cast=str, default="fasteve_database")
SQL_URI = config("FASTEVE_SQL_URI", cast=str, default="sqlite://")
CORS_ORIGINS = config("FASTEVE_CORS_ORIGINS", cast=str, default=None)
CONNECTION_TIMEOUT = config("FASTEVE_CONNECTION_TIMEOUT", cast=int, default=10000)

# default query parameters
QUERY_WHERE = config("FASTEVE_QUERY_WHERE", cast=str, default="where")
QUERY_PROJECTION = config("FASTEVE_QUERY_PROJECTION", cast=str, default="projection")
QUERY_SORT = config("FASTEVE_QUERY_SORT", cast=str, default="sort")
QUERY_PAGE = config("FASTEVE_QUERY_PAGE", cast=str, default="page")
QUERY_MAX_RESULTS = config("FASTEVE_QUERY_MAX_RESULTS", cast=str, default="max_results")
QUERY_EMBEDDED = config("FASTEVE_QUERY_EMBEDDED", cast=str, default="embedded")
QUERY_AGGREGATION = config("FASTEVE_QUERY_AGGREGATION", cast=str, default="aggregate")
