# System imports
from sys import exit
import os
import argparse
import glob
from os.path import join, basename

# xeno imports
from xeno.core.output import print_error
from xeno.core.paths import get_working_directory
from xeno.core.git import get_metadata_from_repo
from xeno.core.editor import run_editor_on_local_path
from xeno.core.configuration import string_to_bool


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

    # Make sure it is still alive
    try:
        os.kill(pid, 0)
    except:
        print_error('Session is not active: {0}'.format(pid))
        exit(1)

    # Find the corresponding repo
    possible_repos = glob.glob(join(
        get_working_directory(),
        'local-*',
        '*'
    ))

    # Go through the repos
    for repo in possible_repos:
        # Grab the metadata
        process_id = get_metadata_from_repo(repo, 'syncProcessId')

        # Check if it matches
        if args.session == process_id:
            # Found it!

            # Check if it is a single file
            remote_is_file = string_to_bool(get_metadata_from_repo(
                repo,
                'remoteIsFile'
            ))

            # Calculate the editor path
            if remote_is_file:
                edit_path = join(repo, basename(get_metadata_from_repo(
                    repo,
                    'remotePath'
                )))
            else:
                edit_path = repo

            # Found it!
            exit(run_editor_on_local_path(edit_path))

    # Couldn't find a match
    print_error('Couldn\'t find specified session: {0}'.format(
        args.session
    ))
    exit(1)
