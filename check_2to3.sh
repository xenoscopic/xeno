#!/bin/bash

find . -name '*.py' | xargs 2to3 -p -x future -x basestring -x imports
