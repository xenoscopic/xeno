# System imports
from sys import exit
import os
import signal
import argparse

# xeno imports
from xeno.core.output import print_error
from xeno.core.sessions import get_sessions


def parse_arguments():
    """Method to parse command line arguments.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(
        description='stop xeno editing sessions',
        usage='xeno-stop [-h|--help] session',
    )

    # Add arguments
    parser.add_argument('session',
                        help='the session number to stop (the first column '
                             'in \'xeno list\')',
                        action='store',
                        nargs='?')

    # Do the parsing
    args = parser.parse_args()

    # Check if the user needs help
    if args.session is None:
        parser.print_help()
        exit(1)

    return args


def main():
    """The stop subcommand handler.

    This method handles the 'stop' subcommand by stopping active xeno sessions.
    """
    # Parse arguments.  If no session is specified, it will exit.
    args = parse_arguments()

    # Convert the session id
    try:
        pid = int(args.session)
    except:
        print_error('Invalid session id: {0}' % args.session)
        exit(1)

    # Grab the sessions
    sessions = get_sessions()

    # Go through the repos
    for session in sessions:
        # Grab the metadata
        process_id = session[0]

        # Check if it matches
        if pid == process_id:
            # Send a SIGTERM to the session
            os.kill(pid, signal.SIGTERM)

            # All done
            exit(0)

    # Couldn't find a match
    print_error('Couldn\'t find specified session: {0}'.format(
        args.session
    ))
    exit(1)
