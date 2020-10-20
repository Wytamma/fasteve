#!/usr/bin/env bash

set -e
set -x

python -m pytest --cov=fasteve --cov=tests
bash ./scripts/lint.sh
