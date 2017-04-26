#!/bin/bash

# Wrapper to execute test.py in venv

cd $(dirname "${0}") || exit1
./venv/bin/python2 ./test.py "${@}"
