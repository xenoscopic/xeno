# System imports
from sys import exit
import argparse


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
    parser.add_argument('path-or-remote',
                        help='the path to edit, either as a local path or '
                             'remote specification',
                        action='store',
                        nargs=1)

    # Do the parsing
    return parser.parse_args()


def main():
    """The edit subcommand handler.

    This method handles the 'edit' subcommand by starting an editing session.
    """
    # Parse arguments
    args = parse_arguments()

    # All done
    exit(0)
