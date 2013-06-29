# Future imports to support fancy print() on Python 2.x
from __future__ import print_function

# System imports
import atexit
import argparse
import uuid
import os
import sys
from sys import exit
import subprocess
import signal

# xeno imports
from ..core.output import print_warning, print_error
from ..core.paths import get_working_directory
from ..core.editor import run_editor_on_local_path
from ..core.protocol import check_for_initialization_token, \
    INITIALIZATION_KEY_IS_FILE, INITIALIZATION_KEY_REMOTE_PATH, \
    INITIALIZATION_KEY_REPOSITORY_PATH
from ..core.git import cloneable_remote_path
from ..core.syncing import start_syncing


def parse_arguments():
    """Method to parse command line arguments.  For the case of SSH, we do this
    only to be able to grab the port argument if it is passed to SSH.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(add_help=False)

    # Add arguments
    parser.add_argument('-p',
                        action='store',
                        dest='port',
                        nargs='?')
    parser.add_argument('user_hostname',
                        action='store',
                        nargs='?')
    parser.add_argument('command',
                        action='store',
                        nargs='?')

    # Do the parsing of the arguments we want
    return parser.parse_known_args()[0]


# Global variable to hold path the SSH monitoring FIFO
_FIFO_PATH = None


# Method to create a FIFO
def create_fifo():
    """This method creates a filesystem-visible FIFO in the xeno working
    directory with a non-conflicting filename.

    If this method fails, it will print an error and exit.  It will set the
    global variables _FIFO_PATH.

    Returns:
        A string representing the fifo path.
    """
    # Grab the working directory
    working_directory = get_working_directory()

    # Create a unique filename
    fifo_path = os.path.join(working_directory, 'fifo-' + uuid.uuid4().hex)

    # Try to make the FIFO, accessible only by the user
    try:
        os.mkfifo(fifo_path, 0660)
    except Exception, e:
        print_error('Unable to create FIFO at path \'{0}\': {1}'.format(
            fifo_path,
            str(e)
        ))
        exit(1)

    # If things succeeded, set the global variable
    global _FIFO_PATH
    _FIFO_PATH = fifo_path

    return fifo_path


# Method to clean up monitoring FIFO on exit
def cleanup_fifo():
    """Tries to clean up the monitoring FIFO, warning the user if it can't.
    """
    # Switch to the global variables
    global _FIFO_PATH

    # _FIFO_PATH the FIFO if it exists
    if _FIFO_PATH is not None:
        try:
            os.remove(_FIFO_PATH)
        except OSError:
            print_warning('Unable to remove FIFO: {0}'.format(_FIFO_PATH))


def main():
    """The ssh subcommand handler.

    This method handles the 'xeno ssh' subcommand by starting an ssh session
    which is xeno-aware.
    """
    # Register the FIFO cleanup method
    atexit.register(cleanup_fifo)

    # Create the FIFO.  This method will exit on failure.
    fifo_path = create_fifo()

    # Parse out the username, hostname, and port from the SSH arguments.  Don't
    # bother handling weird user_hostname cases, SSH will fail before it
    # matters.
    args = parse_arguments()
    username = None
    hostname = None
    port = None
    user_hostname_split = args.user_hostname.split('@')
    if len(user_hostname_split) == 1:
        hostname = user_hostname_split
    elif len(user_hostname_split) == 2:
        username, hostname = user_hostname_split
    if args.port is not None:
        try:
            port = int(args.port)
        except:
            # Don't worry, if it's messed up, SSH will tell the user
            pass

    # Create our subprocesses.  Launch SSH with its output piped to tee, and
    # have tee dump the output to our FIFO.
    # TODO: This is entirely POSIX-specific, but if we want to do it ourselves,
    # we'd have to implement the functionality of tee, which would undoubtedly
    # require some POSIX-specific terminal messing about, and we'd undoubtedly
    # cock it up, so this is easy enough for now.
    ssh = subprocess.Popen(['ssh'] + sys.argv[1:], stdout=subprocess.PIPE)
    tee = subprocess.Popen(['tee', fifo_path], stdin=ssh.stdout)

    # We can now open the FIFO.  We have to do this AFTER setting up the
    # subprocesses, because we are going to open the FIFO in blocking mode, and
    # in the case of named pipes, the open() function will block until data is
    # written to the pipe, which won't happen until after our processes start.
    # We could open in non-blocking mode, but then we woudldn't have the nice
    # readline facility.
    try:
        fifo_file = open(fifo_path, 'r')
    except Exception, e:
        # Kill the child processes
        ssh.kill()
        tee.kill()

        # Bail
        print_error('Unable to open monitoring FIFO \'{0}\': {1}'.format(
            fifo_path,
            str(e)
        ))

    # Now read our FIFO until it runs out, looking for xeno invocations.  We
    # skip this if SSH is just executing a command.
    is_not_command = args.command is None
    while is_not_command:
        # Grab a new line
        line = fifo_file.readline()

        # Check if it is EOF (end of the process)
        if line == '':
            break

        # Check for our marker
        initialization_token = check_for_initialization_token(line)
        if initialization_token is not None:
            # Suspend SSH
            ssh.send_signal(signal.SIGSTOP)

            # Parse up the initialization token
            remote_is_file = initialization_token[INITIALIZATION_KEY_IS_FILE]
            remote_path = initialization_token[INITIALIZATION_KEY_REMOTE_PATH]
            remote_repo_path = \
                initialization_token[INITIALIZATION_KEY_REPOSITORY_PATH]

            # Compute the cloneable path
            cloneable_path = cloneable_remote_path(username,
                                                   hostname,
                                                   port,
                                                   remote_repo_path)

            # Start syncing
            local_path = start_syncing(remote_is_file,
                                       remote_path,
                                       cloneable_path)

            # Launch our editor, if the path is valid
            if local_path is not None:
                run_editor_on_local_path(local_path,
                                         exit_on_no_editor=False)

            # Resume SSH
            ssh.send_signal(signal.SIGCONT)

    # Wait for SSH and tee to finish, that way we don't get a broken pipe if
    # we close the FIFO
    result = ssh.wait()
    tee.wait()

    # Close the FIFO.  It'll be removed from disk automatically at exit
    fifo_file.close()

    # All done, send back SSH's error code
    exit(result)
