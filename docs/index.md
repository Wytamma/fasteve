# Home

![fasteve logo](images/fasteve-logo.svg)

[![PyPi](https://img.shields.io/pypi/v/fasteve.svg)](https://pypi.org/project/fasteve/)
[![testing](https://github.com/Wytamma/fasteve/actions/workflows/testing.yml/badge.svg)](https://github.com/Wytamma/fasteve/actions/workflows/testing.yml)
[![coverage](https://codecov.io/gh/Wytamma/fasteve/branch/master/graph/badge.svg)](https://codecov.io/gh/Wytamma/fasteve)
[![image](https://img.shields.io/github/license/wytamma/fasteve.svg)](https://github.com/Wytamma/fasteve/blob/master/LICENSE)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://img.shields.io/badge/code%20style-black-000000.svg)

Fasteve is a rebuild of [Eve](https://github.com/pyeve/eve) using [FastAPI](https://github.com/tiangolo/fastapi) as a base.

## Installation

<div class="termy">

```console
$ pip install fasteve

---> 100%
```

</div>

## Example

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


<div class="termy">

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

</div>