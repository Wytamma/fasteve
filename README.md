Fasteve
====

Fasteve is a rebuild of Eve using FastAPI as a base instead of Flask.

Fasteve is Simple
-------------

Create a file `main.py` with:
```python
from fasteve import Fasteve, BaseSchema, Resource

class People(BaseSchema):
    name: str

people = Resource(route="people", schema=People)
resources = [people]

app = Fasteve(resources=resources)
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
        "self": {"href": "people", "title": "people"},
        "parent": {"href": "/", "title": "home"},
    },
}
```

All you need to bring your API online is a database, a configuration file
(defaults to ``settings.py``) and a launch script.  Overall, you will find that
configuring and fine-tuning your API is a very simple process.

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
