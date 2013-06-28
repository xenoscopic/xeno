# System imports
from sys import exit
import argparse

# xeno imports
from ..core.output import print_error
from ..core.path import Path
from ..core.editor import launch_editor_on_local_path


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

    # If the path is local, just open it in the editor
    if path.is_local:
        launch_editor_on_local_path(path.file_path, replace=True)

    # All done
    exit(0)
