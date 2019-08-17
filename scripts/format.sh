#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place fasteve tests --exclude=__init__.py
black fastapi tests docs/src
