# System imports
from sys import exit
import os
import argparse
from os.path import join, basename

# xeno imports
from xeno.core.output import print_error
from xeno.core.sessions import get_sessions, XENO_SESSION_LOCAL_PROCESS_ID, \
    XENO_SESSION_LOCAL_REPOSITORY_PATH, XENO_SESSION_REMOTE_PATH, \
    XENO_SESSION_REMOTE_IS_FILE
from xeno.core.editor import run_editor_on_local_path


def parse_arguments():
    """Method to parse command line arguments.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(
        description='resume xeno editing sessions',
        usage='xeno-resume [-h|--help] session',
    )

    # Add arguments
    parser.add_argument('session',
                        help='the session number to resume (the first column '
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
    """The resume subcommand handler.

    This method handles the 'resume' subcommand by resuming active xeno
    sessions.
    """
    # Parse arguments.  If no session is specified, it will exit.
    args = parse_arguments()

    # Convert the session id
    try:
        pid = int(args.session)
    except:
        print_error('Invalid session id: {0}'.format(args.session))
        exit(1)

    # Grab the sessions
    sessions = get_sessions()

    # Go through the sessions
    for session in sessions:
        # Grab the metadata
        process_id = session[XENO_SESSION_LOCAL_PROCESS_ID]

        # Check if it matches
        if pid == process_id:
            # Found it!

            # Check if it is a single file
            remote_is_file = session[XENO_SESSION_REMOTE_IS_FILE]

            # Calculate the editor path
            if remote_is_file:
                edit_path = join(
                    session[XENO_SESSION_LOCAL_REPOSITORY_PATH],
                    basename(
                        session[XENO_SESSION_REMOTE_PATH]
                    )
                )
            else:
                edit_path = session[XENO_SESSION_LOCAL_REPOSITORY_PATH]

            # Found it!
            exit(run_editor_on_local_path(edit_path))

    # Couldn't find a match
    print_error('Couldn\'t find specified session: {0}'.format(
        args.session
    ))
    exit(1)
