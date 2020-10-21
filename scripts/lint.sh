#!/usr/bin/env bash

set -e
set -x

mypy fasteve tests --disallow-untyped-defs
black fasteve tests --check