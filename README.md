![fasteve logo](https://i.ibb.co/Czrk2L9/fasteve-logo.png)

[![PyPi](https://img.shields.io/pypi/v/fasteve.svg)](https://pypi.org/project/fasteve/)
[![testing](https://github.com/Wytamma/fasteve/actions/workflows/testing.yml/badge.svg)](https://github.com/Wytamma/fasteve/actions/workflows/testing.yml)
[![coverage](https://codecov.io/gh/Wytamma/fasteve/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/fasteve)
[![image](https://img.shields.io/github/license/wytamma/fasteve.svg)](https://github.com/Wytamma/fasteve/blob/master/LICENSE)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://img.shields.io/badge/code%20style-black-000000.svg)

Fasteve is a rebuild of [Eve](https://github.com/pyeve/eve) using [FastAPI](https://github.com/tiangolo/fastapi) as a base.

Fasteve is Simple
-------------

Create a file `main.py` with:
```python
from fasteve import Fasteve, MongoModel, Resource

class People(MongoModel):
    name: str

people = Resource(model=People)
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
* Powered by FastAPI ✅
* Emphasis on REST ✅
* Full range of CRUD operations ✅
* Customizable resource endpoints ✅
* Sub Resources ✅
* Pagination ✅
* HATEOAS ✅
* Bulk create ✅
* Data Validation ✅
* Extensible Data Validation ✅
* Unique Fields ✅
* CORS Cross-Origin Resource Sharing ✅
* Read-only by default ✅
* Default Values ✅
* Embedded Resource Serialization ✅
* Event Hooks ✅
* Custom ID Fields ✅
* Alternative ID Fields ✅
* Interactive API docs (provided by Swagger UI) ✅
* Alternative API docs (provided by ReDoc) ✅
* Repeated Background Tasks ✅
* MongoDB Support ✅
* SQL Support ✅
* Predefined Database Filters
* Projections
* JSONP
* Customizable, multiple item endpoints
* Filtering and Sorting
* JSON and XML Rendering
* Conditional Requests
* Data Integrity and Concurrency Control
* Resource-level Cache Control
* API Versioning
* Document Versioning
* Authentication
* Rate Limiting
* File Storage
* GeoJSON
* Internal Resources
* Enhanced Logging
* Operations Log
* MongoDB Aggregation Framework


License
-------
Fasteve is a open source project,
distributed under the `BSD license`


Latest Changes
-

* :sparkles: add SQL support via sqlmodel. PR [#21](https://github.com/Wytamma/fasteve/pull/21) by [@Wytamma](https://github.com/Wytamma).
* :tada: v0.1.3. PR [#20](https://github.com/Wytamma/fasteve/pull/20) by [@Wytamma](https://github.com/Wytamma).
* :sparkles: Add event hooks. PR [#17](https://github.com/Wytamma/fasteve/pull/17) by [@Wytamma](https://github.com/Wytamma).
* :sparkles: break up endpoints. PR [#16](https://github.com/Wytamma/fasteve/pull/16) by [@Wytamma](https://github.com/Wytamma).
* :sparkles: Add PATCH method. PR [#15](https://github.com/Wytamma/fasteve/pull/15) by [@Wytamma](https://github.com/Wytamma).
* :bug: PUT does upsert when ID not found. PR [#14](https://github.com/Wytamma/fasteve/pull/14) by [@Wytamma](https://github.com/Wytamma).
* :art: PUT returns 204 (No Content). PR [#13](https://github.com/Wytamma/fasteve/pull/13) by [@Wytamma](https://github.com/Wytamma).
* :sparkles: Add PUT method. PR [#12](https://github.com/Wytamma/fasteve/pull/12) by [@Wytamma](https://github.com/Wytamma).
* :art: Formatting with Black. PR [#11](https://github.com/Wytamma/fasteve/pull/11) by [@Wytamma](https://github.com/Wytamma).
