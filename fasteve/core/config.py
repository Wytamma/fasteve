from starlette.config import Config

# Config will be read from environment variables and/or ".env" files.
config = Config(".env")

INFO = config("INFO", cast=str, default="_info")
API_VERSION = config("API_VERSION", cast=str, default="0.1")
HATEOAS = config("HATEOAS", cast=bool, default=True)
LINKS = config("LINKS", cast=str, default="_links")
MONGODB_URL = config("MONGODB_URL", cast=str, default="mongodb://$MONGO_USER:$MONGO_PASSWORD@$MONGO_HOST:$MONGO_PORT")
MONGO_DB = config("MONGO_DB", cast=str, default="fasteve_db")
MAX_CONNECTIONS_COUNT  = config("MAX_CONNECTIONS_COUNT", cast=str, default="_links")
MIN_CONNECTIONS_COUNT  = config("MIN_CONNECTIONS_COUNT", cast=str, default="_links")