#!/usr/bin/env bash

SCRIPT_DIR="/home/redhen/NephosTestingSKumar/nephos"

cd $SCRIPT_DIR
screen pipenv run python3 -m nephos start
