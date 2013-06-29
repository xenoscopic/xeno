# System imports
import os
from sys import exit
import argparse

# xeno imports
from ..core.output import print_error
from ..core.path import Path
from ..core.editor import run_editor_on_local_path
from ..core.git import initialize_remote_repository
from ..core.protocol import create_initialization_token, \
    check_for_initialization_token


def parse_arguments():
    """Method to parse command line arguments.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(
        description='edit paths with xeno',
        usage='xeno-edit [-h|--help] [[username@]hostname:[port:]]file_path',
    )

    # Add arguments
    parser.add_argument('path_or_remote',
                        help='the path to edit, either as a local path or '
                             'remote specification',
                        action='store',
                        nargs='?')
    
    # Do the parsing
    args = parser.parse_args()

    # Check if the user needs help
    if args.path_or_remote is None:
        parser.print_help()
        exit(1)

    return args


def main():
    """The edit subcommand handler.

    This method handles the 'edit' subcommand by starting an editing session.
    """
    # Parse arguments.  If not path or remote is specified, this will print
    # help and exit.
    args = parse_arguments()

    # Parse the path or remote
    try:
        path = Path(args.path_or_remote)
    except ValueError:
        print_error('Invalid path or remote specified: {0}'.format(
            args.path_or_remote
        ))

    # Determine if we are running locally or in an SSH session
    in_ssh = os.environ.has_key('SSH_CONNECTION')

    # If the path is local...
    if path.is_local:
        if in_ssh:
            # If we're running in SSH, then we need to create the 'remote'
            # repository for the client to clone and spit out the initialization
            # string.
            repo_path = initialize_remote_repository(path.file_path)
            print(create_initialization_token(repo_path))
            exit(0)
        else:
            # If we're not running in SSH, then the user is just using
            # xeno-edit as their normal editor.
            exit(run_editor_on_local_path(path.file_path))

    # Otherwise the path is remote, so we need to invoke SSH to the remote
    # destination and run the xeno-edit command there to get the clone-able
    # path
    # TODO: Implement

    # All done
    exit(0)
