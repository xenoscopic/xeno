#!/bin/bash

find . -name '*.py' | xargs 2to3 -p
