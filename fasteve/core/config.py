from starlette.config import Config

# Config will be read from environment variables and/or ".env" files.
config = Config(".env")

INFO = config("INFO", cast=str, default="_info")
API_VERSION = config("API_VERSION", cast=str, default="0.1")
HATEOAS = config("HATEOAS", cast=bool, default=True)
LINKS = config("LINKS", cast=str, default="_links")
