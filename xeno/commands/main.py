# System imports
import sys
from sys import exit
import os
import argparse

# xeno imports
from ..version import XENO_VERSION, STRINGIFY_VERSION
from ..core.output import print_warning, print_error


class HelpAction(argparse.Action):
    """Custom argparse action to handle store help flag but not print help
    automatically, in case we need to dispatch '--help' to a subcommand.

    This class is necessary because argparse.ArgumentParser.add_argument does
    not support adding a help argument with action=store_true.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        # Mark the help flag
        namespace.help = True


def parse_arguments():
    """Method to parse command line arguments.

    This function will parse command line arguments using the argparse module.

    Returns:
        A tuple of the form (known_args, unknown_args).
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(
        description='synchronous remote file editing',
        usage='xeno [-h|--help] [--version] <subcommand> [arguments]',
        add_help=False
    )
    parser.add_argument('-h',
                        '--help',
                        nargs=0,
                        action=HelpAction,
                        help='show this help message and exit')
    parser.add_argument('--version',
                        action='version',
                        version=STRINGIFY_VERSION(XENO_VERSION))

    # Add the subcommand group with a description of commonly-used commands
    subcommand_group = parser.add_argument_group(
        title='subcommands',
        description='xeno farms out its work to a variety of subcommands.  '
        'The primary subcommands are \'config\' and \'edit\'.  To view help '
        'information on a particular subcommand, use \'xeno '
        'EXAMPLE_SUBCOMMAND --help\'.'
    )

    # Add the subcommand argument, hiding its help information
    subcommand_group.add_argument('subcommand',
                                  action='store',
                                  nargs='?',
                                  help=argparse.SUPPRESS)

    # Do the parsing
    known_args, unknown_args = parser.parse_known_args()

    # If the user has not specified a subcommand, print help, and exit
    # with failure/success depending on whether or not they asked for help
    if known_args.subcommand is None:
        parser.print_help()
        if known_args.help:
            exit(0)
        else:
            exit(1)

    # At this point, the user must have specified a subcommand.  If they have
    # requested help, then we should pass the help flag through to the
    # subcommand.
    if known_args.help:
        unknown_args = ['-h'] + unknown_args

    return known_args, unknown_args


def validate_subcommand(subcommand):
    """Validates that the specified subcommand name points to a valid
    executable.

    This method will look for an executable in the path with the name:

        'xeno-subcommand'

    replacing 'subcommand' with the value provided.  If no match is found, this
    method will print an error and exit.

    Args:
        subcommand: The name of the subcommand to test

    Returns:
        The full path of the executable.
    """
    # Compute the full executable name
    executable_name = 'xeno-' + subcommand
    if sys.platform == 'win32':
        executable_name += '.exe'

    # Create a macro to check for executability
    executable = lambda p: os.path.isfile(p) and os.access(p, os.X_OK)

    # Loop through the user's path
    for path in os.environ['PATH'].split(os.pathsep):
        path = path.strip('"')
        if executable(os.path.join(path, executable_name)):
            return executable_name

    # No good match
    print_error('Invalid xeno subcommand: \'{0}\''.format(subcommand))
    exit(1)


def dispatch_subcommand(executable_name, arguments):
    """Starts a specified subcommand executable with the arguments provided.

    This method will replace this process with the one denoted by the
    subcommand and feed it the specified arguments.

    Args:
        executable_name: The executable name of the subcommand, as provided by
            validate_subcommand
        arguments: The list of arguments to pass to the subcommand
    """
    # Call execvp to replace this executable with the executable name
    # specified.  Python will look through PATH to find the appropriate
    # executable path.  The executable name should be provided as the first
    # item in the argument list.  Strangely, Python seems to replace whatever
    # value is passed here with the full executable path.  Go figure.
    os.execvp(executable_name, [executable_name] + arguments)


def main():
    """Main entry point for xeno program.

    This function is invoked when the module is being executed directly.
    """
    # Parse command line arguments.  If no subcommand is specified, this will
    # print help and exit.
    known_args, unknown_args = parse_arguments()

    # Check if the specified command is valid
    executable_name = validate_subcommand(known_args.subcommand)

    # Dispatch the remaining arguments to the subcommand
    dispatch_subcommand(executable_name, unknown_args)
