#!/usr/bin/env bash

NEPHOS_DIR=$(dirname $0)

cd ${NEPHOS_DIR}
export PYTHON_BIN_PATH="$(python3 -m site --user-base)/bin"
export PATH="$PATH:$PYTHON_BIN_PATH"
screen pipenv run python3 -m nephos start
