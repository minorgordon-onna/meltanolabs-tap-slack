#!/bin/bash

cd $(dirname "$0")/..

poetry lock && poetry install --remove-untracked
