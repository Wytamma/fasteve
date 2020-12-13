![fasteve logo](https://i.ibb.co/Czrk2L9/fasteve-logo.png)

[![PyPi](https://img.shields.io/pypi/v/fasteve.svg)](https://pypi.org/project/fasteve/)
[![Test](https://github.com/Wytamma/fasteve/workflows/Test/badge.svg)](https://github.com/Wytamma/fasteve/actions?query=workflow%3ATest)
[![coverage](https://codecov.io/gh/Wytamma/fasteve/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/fasteve)
[![Lint](https://github.com/Wytamma/fasteve/workflows/Lint/badge.svg)](https://github.com/Wytamma/fasteve/actions?query=workflow%3ALint)
[![image](https://img.shields.io/github/license/wytamma/fasteve.svg)](https://img.shields.io/github/license/wytamma/fasteve)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://img.shields.io/badge/code%20style-black-000000.svg)

Fasteve is a rebuild of [Eve](https://github.com/pyeve/eve) using [FastAPI](https://github.com/tiangolo/fastapi) as a base.

Fasteve is Simple
-------------

Create a file `main.py` with:
```python
from fasteve import Fasteve, BaseSchema, Resource

class People(BaseSchema):
    name: str

people = Resource(schema=People)
resources = [people]

app = Fasteve(resources=resources)
```

Start a database ([mongodb default](https://hub.docker.com/_/mongo)):
```console
$ docker run --rm -p 27017:27017 mongo
```

Run the server with:
```console
$ uvicorn main:app --reload
```

The API is now live, ready to be consumed:

```console
$ curl -i http://localhost:8000/people
HTTP/1.1 200
...
{
    "_data": [],
    "_meta": {"max_results": 25, "total": 0, "page": 1},
    "_links": {
        "self": {"href": "/people", "title": "people"},
        "parent": {"href": "/", "title": "home"},
    },
}
```

Features (TODO)
---------------
* Emphasis on REST ✅
* Full range of CRUD operations ✅
* Customizable resource endpoints ✅
* Sub Resources ✅
* Customizable, multiple item endpoints
* Filtering and Sorting
* Pagination ✅
* HATEOAS ✅
* JSON and XML Rendering
* Conditional Requests
* Data Integrity and Concurrency Control
* Bulk Inserts ✅
* Data Validation ✅
* Extensible Data Validation ✅
* Unique Fields ✅
* Resource-level Cache Control
* API Versioning
* Document Versioning
* Authentication
* CORS Cross-Origin Resource Sharing ✅
* JSONP
* Read-only by default ✅
* Default Values ✅
* Predefined Database Filters
* Projections
* Embedded Resource Serialization ✅
* Event Hooks ✅
* Rate Limiting
* Custom ID Fields ✅
* Alternative ID Fields ✅
* File Storage
* GeoJSON
* Internal Resources
* Enhanced Logging
* Operations Log
* Interactive API docs (provided by Swagger UI) ✅
* Alternative API docs (provided by ReDoc) ✅
* Repeated Background Tasks ✅
* MongoDB Aggregation Framework
* MongoDB Support ✅
* SQL Support
* Powered by FastAPI ✅

License
-------
Fasteve is a open source project,
distributed under the `BSD license`


Latest Changes
-

* :sparkles: Add event hooks. PR [#17](https://github.com/Wytamma/fasteve/pull/17) by [@Wytamma](https://github.com/Wytamma).
* :sparkles: break up endpoints. PR [#16](https://github.com/Wytamma/fasteve/pull/16) by [@Wytamma](https://github.com/Wytamma).
* :sparkles: Add PATCH method. PR [#15](https://github.com/Wytamma/fasteve/pull/15) by [@Wytamma](https://github.com/Wytamma).
* :bug: PUT does upsert when ID not found. PR [#14](https://github.com/Wytamma/fasteve/pull/14) by [@Wytamma](https://github.com/Wytamma).
* :art: PUT returns 204 (No Content). PR [#13](https://github.com/Wytamma/fasteve/pull/13) by [@Wytamma](https://github.com/Wytamma).
* :sparkles: Add PUT method. PR [#12](https://github.com/Wytamma/fasteve/pull/12) by [@Wytamma](https://github.com/Wytamma).
* :art: Formatting with Black. PR [#11](https://github.com/Wytamma/fasteve/pull/11) by [@Wytamma](https://github.com/Wytamma).
