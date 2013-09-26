# Check the python version before proceeding too far
from xeno.version import check_python_version, XENO_VERSION, STRINGIFY_VERSION
check_python_version()


# Export the xeno version
__version__ = STRINGIFY_VERSION(XENO_VERSION)
