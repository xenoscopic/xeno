# System imports
import sys
from sys import exit
import argparse

# xeno imports
from ..core.output import print_warning, print_error
from ..core.configuration import configuration_file_path, load_configuration, \
    save_configuration


def parse_arguments():
    """Method to parse command line arguments.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(
        description='view/edit xeno configuration information',
        usage='xeno-config [-h|--help] [-c|--clear] [key] [value]',
    )

    # Add arguments
    parser.add_argument('-c',
                        '--clear',
                        action='store_true',
                        dest='clear')
    parser.add_argument('key',
                        help='the configuration key to view/edit',
                        action='store',
                        nargs='?')
    parser.add_argument('value',
                        help='the value to set for the configuration',
                        action='store',
                        nargs='?')

    # Do the parsing
    return parser.parse_args()


def main():
    """The config subcommand handler.

    This method handles the 'config' subcommand by either showing, editing, or
    clearing the specified configuration key, and then exiting.
    """
    # Parse arguments
    args = parse_arguments()

    # Load the configuration
    configuration = load_configuration()

    # If the user has not specified a key, then print the current configuration
    if args.key is None:
        # Check if the user has specified a '--clear' option.  If they have,
        # inform them that this is not respected without specifying a key
        # because it is dangerous.
        if args.clear:
            print_warning(
                'Specifying \'config --clear\' without specifying a key is '
                'prohibited, because you can easily destroy your '
                'configuration.  If you really want to clear all of your '
                'settings, you can delete your configuration file at '
                '\'{0}\''.format(
                    configuration_file_path(False)
                )
            )
            exit(1)

        # Otherwise, assume they just want to see all configuration values
        configuration.write(sys.stdout)
        exit(0)

    # Parse up the key
    try:
        section, option = args.key.split('.')
    except:
        print_error(
            'Invalid configuration key \'{0}\''.format(
                args.key
            )
        )
        exit(1)

    # If they have specified a key, but have not specified a value, then either
    # clear or print the value of the key
    if args.value is None:
        # If clear has been specified, then clear the value and exit
        if args.clear:
            try:
                # Remove the specific option
                configuration.remove_option(section, option)

                # If there are no keys left in the section, clean it up
                if len(configuration.items(section)) == 0:
                    configuration.remove_section(section)
            except:
                # This will only fail if the section doesn't exist, in which
                # case we can just consider it cleared anyway
                pass
            save_configuration(configuration)
            exit(0)

        # Otherwise, print the value of the key
        try:
            print(configuration.get(section, option))
        except:
            print_error(
                'No configuration specified for key \'{0}\''.format(
                    args.key
                ),
                file=sys.stderr
            )
        exit(0)

    # At this point, they must have specified a value.  If they have also
    # specified '--clear', warn them that it doesn't make sense to clear and
    # set a value
    if args.clear:
        print_warning(
            'You have specified a value (\'{0}\') for the key (\'{1}\'), but '
            'you have also specified the \'--clear\' option.  If you want to '
            'clear the value, specify only \'--clear\'.  If you want to '
            'specify the value, then provide only the value but do not use '
            '\'--clear\'.'.format(
                args.value,
                args.key
            )
        )
        exit(1)

    # They must be wanting to write the value, so make sure the section exists
    if not configuration.has_section(section):
        configuration.add_section(section)

    # Write the specified value
    configuration.set(section, option, args.value)
    save_configuration(configuration)

    # All done
    exit(0)
