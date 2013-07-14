# System imports
from sys import exit
import os
from os.path import realpath, normpath
import argparse
from itertools import chain
import subprocess

# xeno imports
from xeno.core.output import print_error
from xeno.core.paths import Path
from xeno.core.editor import run_editor_on_local_path
from xeno.core.git import initialize_remote_repository, cloneable_remote_path
from xeno.core.protocol import create_initialization_token, \
    check_for_initialization_token, INITIALIZATION_KEY_IS_FILE, \
    INITIALIZATION_KEY_REMOTE_PATH, INITIALIZATION_KEY_REPOSITORY_PATH
from xeno.version import XENO_VERSION, STRINGIFY_VERSION
from xeno.core.syncing import start_syncing


def parse_arguments():
    """Method to parse command line arguments.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(
        description='edit paths with xeno',
        usage='xeno-edit [-h|--help] [[username@]hostname:[port:]]file_path \n'
              '\t[-i|--ignore <ignore> [<ignore> ...]]',
    )

    # Add arguments
    parser.add_argument('path_or_remote',
                        help='the path to edit, either as a local path or '
                             'remote specification',
                        action='store',
                        nargs='?')
    parser.add_argument('-i',
                        '--ignore',
                        action='append',
                        nargs='+',
                        default=[],
                        help='add exclude paths in gitignore format, '
                             'including \'!\' values',
                        metavar='<ignore>')
    parser.add_argument('--client-version',
                        action='store',
                        nargs=1,
                        help=argparse.SUPPRESS,
                        dest='client_version')

    # Do the parsing
    args = parser.parse_args()

    # Join all the ignore paths
    args.ignore = list(chain(*args.ignore))

    # Check if the user needs help
    if args.path_or_remote is None:
        parser.print_help()
        exit(1)

    return args


def initialization_token_from_remote_path(remote_path, ignore_paths):
    """Remotely executes xeno-edit on the remote path and returns the
    initialization token path or exits.

    Args:
        remote_path: The xeno.core.paths.Path object representing the remote
            path
        ignore_paths: A list of ignore entries to pass to the remote repository

    Returns:
        The initialization token dictionary on success, exits on failure.
    """
    # Construct the command list
    command_list = ['ssh']

    # If there is a port, add the flag
    if remote_path.port is not None:
        command_list += ['-p', str(remote_path.port)]

    # Add the username/hostname
    if remote_path.username is not None:
        command_list.append('{0}@{1}'.format(
            remote_path.username,
            remote_path.hostname
        ))
    else:
        command_list.append(remote_path.hostname)

    # Add the xeno edit command, escaping any spaces in the remote path, and
    # passing any ignore paths
    ignore_flags = ''
    if ignore_paths:
        ignore_flags = ' --ignore {0}'.format(
            ' '.join(ignore_paths)
        )
    command_list.append('xeno-edit {0}{1} {2}'.format(
        remote_path.file_path.replace(' ', '\\ '),
        ignore_flags,
        '--client-version {0}'.format(
            STRINGIFY_VERSION(XENO_VERSION)
        )
    ))

    # Execute the subprocess on the remote.  If it fails, its output should be
    # insightful.
    try:
        output = subprocess.check_output(command_list,
                                         stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print_error('Trying to initialize over SSH failed: {0}'.format(
            e.output
        ))
        exit(1)

    # Look for a token
    initialization_token = check_for_initialization_token(output)
    if initialization_token is None:
        print_error('Unable to get initialization token')
        exit(1)

    return initialization_token


def main():
    """The edit subcommand handler.

    This method handles the 'edit' subcommand by starting an editing session.
    """
    # Parse arguments.  If no path or remote is specified, this will print help
    # and exit.
    args = parse_arguments()

    # Parse the path or remote
    try:
        path = Path(args.path_or_remote)
    except ValueError:
        print_error('Invalid path or remote specified: {0}'.format(
            args.path_or_remote
        ))

    # Determine if we are running locally or in an SSH session
    in_ssh = 'SSH_CONNECTION' in os.environ

    # If the path is local...
    if path.is_local:
        if in_ssh:
            # If we're running in SSH, then we need to create the 'remote'
            # repository for the client to clone and spit out the
            # initialization string.  First though, we need to make sure we
            # normalize the path for when we create our initialization token,
            # since the local xeno will rely on the remote end to provide a
            # reasonable value.
            edit_path = realpath(normpath(path.file_path))
            repo_path = initialize_remote_repository(edit_path, args.ignore)
            print(create_initialization_token(edit_path, repo_path))
            exit(0)
        else:
            # If we're not running in SSH, then the user is just using
            # xeno-edit as their normal editor.
            exit(run_editor_on_local_path(path.file_path))

    # Otherwise the path is remote, so we need to invoke SSH to the remote
    # destination and run the xeno-edit command there to get the clone-able
    # path.  This method will exit if it fails.
    initialization_token = initialization_token_from_remote_path(
        path,
        args.ignore
    )

    # Parse up the initialization token
    remote_is_file = initialization_token[INITIALIZATION_KEY_IS_FILE]
    remote_path = initialization_token[INITIALIZATION_KEY_REMOTE_PATH]
    remote_repo_path = \
        initialization_token[INITIALIZATION_KEY_REPOSITORY_PATH]

    # Compute the cloneable path
    cloneable_path = cloneable_remote_path(path.username,
                                           path.hostname,
                                           path.port,
                                           remote_repo_path)

     # Start syncing
    local_path = start_syncing(remote_is_file,
                               remote_path,
                               cloneable_path)

    # Validate the path
    if local_path is None:
        exit(1)

    # Launch our editor
    exit(run_editor_on_local_path(local_path))
