# System imports
from sys import exit
import os
import argparse
import uuid

# xeno imports
from ..core.output import print_error
from ..core.paths import get_working_directory
from ..core.git import clone, add_metadata_to_repo


def parse_arguments():
    """Method to parse command line arguments.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(
        description='do a remote synchronization session with xeno (this '
                    'subcommand is not meant for direct use)',
        usage='xeno-sync [-h|--help]',
    )

    # Add arguments
    parser.add_argument('-f',
                        '--file',
                        action='store_true',
                        help='indicates the remote path is a file',
                        dest='file')
    parser.add_argument('-r',
                        '--remote-path',
                        action='store',
                        nargs=1,
                        required=True,
                        help='the remote path being edited',
                        dest='remote_path')
    parser.add_argument('-c',
                        '--clone-url',
                        action='store',
                        nargs=1,
                        required=True,
                        help='the Git clone URL',
                        dest='clone_url')

    # Do the parsing
    return parser.parse_args()


def main():
    """The sync subcommand handler.

    This method handles the 'sync' subcommand by forking off a daemon to watch
    a particular local repository and synchronize back to the remote.
    """
    # Parse arguments
    args = parse_arguments()

    # Extract them
    remote_is_file = args.file
    remote_path = args.remote_path[0]
    clone_url = args.clone_url[0]

    # Grab the working directory
    working_directory = get_working_directory()

    # Create a unique directory we can use as the PARENT of the repo
    repo_container = os.path.join(working_directory,
                                  'local-' + uuid.uuid4().hex)
    try:
        os.makedirs(repo_container, 0700)
    except:
        print_error('Unable to create repository parent')
        exit(1)

    # Figure out what we're going to call the repo directory
    repo_directory_name = ('remote'
                           if remote_is_file
                           else os.path.basename(remote_path))
    repo_path = os.path.join(repo_container, repo_directory_name)

    # Clone the remote URL
    clone(clone_url, repo_path)

    # Set metadata on the local repo
    add_metadata_to_repo(repo_path, 'remoteIsFile', str(remote_is_file))
    add_metadata_to_repo(repo_path, 'remotePath', remote_path)
    add_metadata_to_repo(repo_path, 'cloneUrl', clone_url)

    # TODO: Daemonize

    # Print the local repo path
    print(repo_path)
