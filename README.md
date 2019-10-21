Fasteve
====

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
    "data": [],
    "meta": {"max_results": 25, "total": 0, "page": 1},
    "links": {
        "self": {"href": "/people", "title": "people"},
        "parent": {"href": "/", "title": "home"},
    },
}
```

Features (TODO)
---------------
* Emphasis on REST
* Full range of CRUD operations
* Customizable resource endpoints
* Customizable, multiple item endpoints
* Filtering and Sorting
* Pagination
* HATEOAS
* JSON and XML Rendering
* Conditional Requests
* Data Integrity and Concurrency Control
* Bulk Inserts
* Data Validation
* Extensible Data Validation
* Resource-level Cache Control
* API Versioning
* Document Versioning
* Authentication
* CORS Cross-Origin Resource Sharing
* JSONP
* Read-only by default
* Default Values
* Predefined Database Filters
* Projections
* Embedded Resource Serialization
* Event Hooks
* Rate Limiting
* Custom ID Fields
* File Storage
* GeoJSON
* Internal Resources
* Enhanced Logging
* Operations Log
* MongoDB Aggregation Framework
* MongoDB and SQL Support
* Powered by FastAPI

License
-------
Fasteve is a open source project,
distributed under the `BSD license`
