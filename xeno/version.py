# System imports
import sys


# Version constants
XENO_VERSION = (0, 0, 1)
XENO_MIN_PYTHON_VERSION = (2, 7, 0)


# Versioning macros
STRINGIFY_VERSION = lambda v: '.'.join((str(i) for i in v))


def check_python_version():
    """Checks that the user is running the minimum-required Python version.

    This method will use the sys module to determine the python version the
    user is running, and exit if it is less than the minimum required version.
    """
    # Grab the version from sys
    PYTHON_VERSION = sys.version_info[0:3]

    # If it is insufficient, print an error message and bail.  We use the
    # direct interface to STDERR because the output module may not work on
    # older versions of python.
    if PYTHON_VERSION < XENO_MIN_PYTHON_VERSION:
        sys.stderr.write(
            'ERROR: Your version of python ({0}) is too old.  The minimum '
            'required version is {1}.'.format(
                STRINGIFY_VERSION(PYTHON_VERSION),
                STRINGIFY_VERSION(XENO_MIN_PYTHON_VERSION)
            )
        )
        sys.exit(1)
