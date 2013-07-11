# System imports
from sys import exit

# xeno imports
from xeno.core.sessions import get_sessions


def main():
    """The list subcommand handler.

    This method handles the 'list' subcommand by listing active xeno sessions.
    """
    # Get all sessions
    sessions = get_sessions()

    # Loop through each one and print out the metadata
    for session in sessions:
        print('{0}: {1} ({2}{3})'.format(
            session[0],
            session[1],
            session[2] + '@' if session[2] else '',
            session[3]
        ))

    # All done
    exit(0)
