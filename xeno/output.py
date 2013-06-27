# Future imports to support fancy print() on Python 2.x
from __future__ import print_function

# System imports
import sys


def print_warning(message):
    print('WARNING: ' + message, file=sys.stderr)


def print_error(message):
    print('ERROR: ' + message, file=sys.stderr)
