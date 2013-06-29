# System imports
import re
from os.path import isfile
import json
import base64

# xeno imports
from ..version import XENO_VERSION, STRINGIFY_VERSION


# Compile the token recognition regex.  We use non-greedy matching to avoid
# matching multiple initializations in case they somehow arrive.
_TOKEN_REGEX = re.compile('\A<xeno-init>(.*?)</xeno-init>')


# Required keys for the initialization dictionary (they must be strings,
# the JSON module will decode them as strings)
INITIALIZATION_KEY_REMOTE_VERSION = '0'
INITIALIZATION_KEY_IS_FILE = '1'
INITIALIZATION_KEY_REMOTE_PATH = '2'
INITIALIZATION_KEY_REPOSITORY_PATH = '3'


def create_initialization_token(path, repo_path):
    """Creates a token that can be recognized for path initialization by the
    client.

    Args:
        path: The path to the file on the remote machine
        repo_path: The path to the repository on the remote machine
    Returns:
        A string representation of the token that must be printed on its own
        line with no preceeding or tailing characters.
    """
    # Create the dictionary
    d = {
        INITIALIZATION_KEY_REMOTE_VERSION: STRINGIFY_VERSION(XENO_VERSION),
        INITIALIZATION_KEY_IS_FILE: isfile(path),
        INITIALIZATION_KEY_REMOTE_PATH: path,
        INITIALIZATION_KEY_REPOSITORY_PATH: repo_path
    }

    # Convert to JSON
    j = json.dumps(d)

    # Base64 encode (remove auto-added-newline and undo the split-on-newline
    # every 76 characters)
    b = ''.join(base64.encodestring(j).strip().split('\n'))

    return '<xeno-init>{0}</xeno-init>'.format(b)


def check_for_initialization_token(text):
    """Looks for a xeno initialization token in text.

    Args:
        text: The text to check

    Returns:
        A string representing the remote repository path, if any, or None if
        there is no initialization token in the text.
    """
    # See if there is a match
    global _TOKEN_REGEX
    match = _TOKEN_REGEX.match(text)

    # If there was no match, give up
    if match is None:
        return None

    # If there was a match, grab it (it should be base64)
    b = match.group(1)

    # Try to base64-decode into JSON
    try:
        j = base64.decodestring(b)
    except:
        return None

    # Try to decode the JSON object
    try:
        d = json.loads(j)
    except:
        return None

    return d
