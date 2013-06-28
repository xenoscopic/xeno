#!/bin/bash

find . -name '*.py' ! -name 'distribute_setup.py' | xargs pep8
