#!/usr/bin/env bash

set -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place fasteve tests --exclude=__init__.py
black fasteve tests
