#!/bin/bash

# Wrapper to execute surfboard.py in venv

cd $(dirname "${0}") || exit1
./venv/bin/python2 ./surfboard.py "${@}"
