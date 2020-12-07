#!/usr/bin/env bash

set -e
set -x

mypy fasteve --disallow-untyped-defs
black fasteve --check