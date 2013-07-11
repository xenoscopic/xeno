# System imports
from sys import exit
try:
    # Python 2.x
    from urlparse import urlparse
except ImportError:
    # Python 3.x
    from urllib.parse import urlparse

# xeno imports
from xeno.core.sessions import get_sessions, XENO_SESSION_LOCAL_PROCESS_ID, \
    XENO_SESSION_REMOTE_CLONE_URL, XENO_SESSION_REMOTE_PATH


def main():
    """The list subcommand handler.

    This method handles the 'list' subcommand by listing active xeno sessions.
    """
    # Get all sessions
    sessions = get_sessions()

    # Loop through each one and print out the metadata
    for session in sessions:
        # Grab the clone URL and chop it up
        clone_url = urlparse(session[XENO_SESSION_REMOTE_CLONE_URL])

        # Compute user/hostname
        username = clone_url.username + '@' if clone_url.username else ''

        print('{0}: {1} ({2}{3})'.format(
            session[XENO_SESSION_LOCAL_PROCESS_ID],
            session[XENO_SESSION_REMOTE_PATH],
            username,
            clone_url.hostname
        ))

    # All done
    exit(0)
