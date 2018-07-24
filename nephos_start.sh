#!/usr/bin/env bash

SCRIPT_DIR="/home/redhen/NephosTestingSKumar/nephos"

cd $SCRIPT_DIR
pipenv run python3 -m nephos init
screen pipenv run python3 -m nephos start
