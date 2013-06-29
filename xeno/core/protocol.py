# System imports
import re


# Compile the token recognition regex.  We use non-greedy matching to avoid
# matching multiple initializations in case they somehow arrive.
_TOKEN_REGEX = re.compile('<xeno-init>(.*?)</xeno-init>')


def create_initialization_token(repo_path):
    """Creates a token that can be recognized for path initialization by the
    client.

    Args:
        repo_path: The path to the repository on the remote machine
    Returns:
        A string representation of the token that must be printed on its own
        line with no preceeding or tailing characters.
    """
    return '<xeno-init>{0}</xeno-init>'.format(repo_path)


def check_for_initialization_token(line):
    """Looks for a xeno initialization token in a line of output.

    Args:
        line: The line to check, with no trailing whitespace (including
            newlines)

    Returns:
        A string representing the remote repository path, if any, or None if
        there is no initialization token in the line.
    """
    # See if there is a match
    global _TOKEN_REGEX
    match = _TOKEN_REGEX.match(line)
    
    # If there was no match, give up
    if match is None:
        return None

    # If there was a match, return it
    return match.group(1)
