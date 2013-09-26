# System imports
from sys import exit
import os
import signal
import argparse

# xeno imports
from xeno.core.output import print_error
from xeno.core.sessions import get_sessions, XENO_SESSION_LOCAL_PROCESS_ID


def parse_arguments():
    """Method to parse command line arguments.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(
        description='stop xeno editing sessions',
        usage='xeno-stop [-h|--help] [-a|--all] [session]',
    )

    # Add arguments
    parser.add_argument('-a',
                        '--all',
                        help='stop all active xeno sessions',
                        action='store_true',
                        dest='all')
    parser.add_argument('session',
                        help='the session number to stop (the first column '
                             'in \'xeno list\')',
                        action='store',
                        nargs='?')

    # Do the parsing
    args = parser.parse_args()

    # Check if the user needs help
    if args.session is None and not args.all:
        parser.print_help()
        exit(1)

    return args


def main():
    """The stop subcommand handler.

    This method handles the 'stop' subcommand by stopping active xeno sessions.
    """
    # Parse arguments.  If no session is specified, it will exit.
    args = parse_arguments()

    # Convert the session id if we're not doing all
    try:
        pid = int(args.session) if not args.all else 0
    except:
        print_error('Invalid session id: {0}' % args.session)
        exit(1)

    # Grab the sessions
    sessions = get_sessions()

    # Go through the sessions
    for session in sessions:
        # Grab the metadata
        process_id = session[XENO_SESSION_LOCAL_PROCESS_ID]

        # If we are ending all sessions, or this session's process id matches
        # the requested session id, end it
        if args.all or (pid == process_id):
            # Send a SIGTERM to the session
            # NOTE: Make sure to use process_id and NOT pid since pid will be 0
            # for stop all
            os.kill(process_id, signal.SIGTERM)

            # If we're not ending all sessions, we must have stopped the
            # requested one, so bail
            if not args.all:
                exit(0)

    # If the user requested all sessions be ended, we have done our job
    if args.all:
        exit(0)

    # Otherwise, we couldn't find a match
    print_error('Couldn\'t find specified session: {0}'.format(
        args.session
    ))
    exit(1)
