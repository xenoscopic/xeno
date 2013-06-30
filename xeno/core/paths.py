# System imports
from sys import exit
from os import makedirs
from os.path import join, expanduser, exists, isdir

# xeno imports
from xeno.core.configuration import get_configuration
from xeno.core.output import print_error


def get_working_directory():
    """Returns the working path for xeno.

    This method returns a path to the xeno working directory, either loading
    it from the configuration or using the default value of ~/.xeno.  This
    method will create the directory if it doesn't exist, and if it is unable
    to create the directory, it will print an error and exit.

    Returns:
        A string representing the path to the xeno working directory.
    """
    # Grab the xeno configuration
    configuration = get_configuration()

    # See if the user has specified the core.workingDirectory setting
    path = None
    if configuration.has_option('core', 'workingDirectory'):
        path = configuration.get('core', 'workingDirectory')

    # If there was no path in the configuration, use the default value
    if path is None:
        path = join(expanduser('~'), '.xeno')

    # Check if the directory exists
    if exists(path):
        if isdir(path):
            return path
        else:
            print_error('xeno working path exists and is not a directory')
            exit(1)

    # If it doesn't exist, try to create it
    try:
        makedirs(path, 0o700)
    except OSError as e:
        print_error('Unable to create xeno working directory: {0}'.format(
            str(e)
        ))
        exit(1)

    return path


class Path(object):
    """Reprents a (possibly remote) path specification.

    This class parses a path of the format:

        [[username@]hostname:[port:]]file_path,

    providing all relevant metadata via convenient accessors.
    """

    def __init__(self, specification):
        """Initializes a new instance of the Path class.

        Args:
            specification: The path specification in the form
                [username@]hostname:[port:]]file_path
        """
        # Validate the object which has been passed in
        if not isinstance(specification, basestring):
            raise TypeError('The specification argument must be a string type')

        # Set up initial values
        self.__username = None
        self.__hostname = None
        self.__port = None
        self.__file_path = None

        # Track the remaining unparsed section of the string
        remaining = specification

        # See if there is a username
        username_split = remaining.split('@')
        if len(username_split) == 1:
            # There is no username specified
            pass
        elif len(username_split) == 2:
            # There is a username specified
            self.__username = username_split[0]
            remaining = username_split[1]
        else:
            # There were multiple '@' symbols
            raise ValueError(
                'Invalid specification: {0}'.format(
                    specification
                )
            )

        # Parse up the rest, which will be colon-delimited
        remaining_split = remaining.split(':')
        if len(remaining_split) == 1:
            # There is just a local path specified
            self.__file_path = remaining_split[0]
        elif len(remaining_split) == 2:
            # There is a hostname and file path specified
            self.__hostname = remaining_split[0]
            self.__file_path = remaining_split[1]
        elif len(remaining_split) == 3:
            # There is a hostname, port, and file path specified
            self.__hostname = remaining_split[0]
            try:
                self.__port = int(remaining_split[1])
            except:
                # The port was not an integer
                raise ValueError(
                    'Invalid port specification: {0}'.format(
                        specification
                    )
                )
            # TODO: Add port range validation?
            self.__file_path = remaining_split[2]
        else:
            # There were too many colons
            raise ValueError(
                'Invalid specification: {0}'.format(
                    specification
                )
            )

        # Make sure path is non-empty
        if self.__file_path == '':
            raise ValueError(
                'File path cannot be empty in specification: {0}'.format(
                    specification
                )
            )

        # Make sure the username has not been specified if there is no hostname
        if self.__hostname is None and self.__username is not None:
            raise ValueError(
                'Invalid specification of username without hostname: '
                '{0}'.format(
                    specification
                )
            )

    @property
    def username(self):
        """Returns the username of the path, if any, or None.
        """
        return self.__username

    @property
    def hostname(self):
        """Returns the hostname of the path, if any, or None.
        """
        return self.__hostname

    @property
    def port(self):
        """Returns the port of the path, if any, or None.
        """
        return self.__port

    @property
    def file_path(self):
        """Returns the file_path portion of the path.
        """
        return self.__file_path

    @property
    def is_local(self):
        """Returns whether or not the path is local (this does not imply
        existence).
        """
        return self.__hostname is None
