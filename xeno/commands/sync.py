# System imports
from sys import exit
import sys
import os
import argparse
import uuid
from shutil import rmtree
import signal
import time

# xeno imports
from ..core.output import print_error
from ..core.configuration import get_configuration
from ..core.paths import get_working_directory
from ..core.git import clone, add_metadata_to_repo, sync_local_with_remote, \
    self_destruct_remote


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


def daemonize():
    """Forks the process into a daemon.

    This method uses the UNIX double-fork trick to ensure the daemon process
    is attached to init and does not reacquire a TTY.  This method only returns
    in the second forked process.
    """
    # TODO: Add some more error checking in here...

    # Do the first fork
    if os.fork() > 0:
        # This is the first parent, exit calmly
        # Recommended exit method on fork()
        os._exit(0)

    # We must be in the first child, decouple from the original parent
    os.chdir('/')
    os.setsid()
    os.umask(0)

    # Flush the original parent output
    sys.stdin.flush()
    sys.stdout.flush()
    sys.stderr.flush()

    # Do the second fork
    if os.fork() > 0:
        # This is the intermediate, exit calmly
        # Recommended exit method on fork()
        os._exit(0)

    # Otherwise, we're in the second child, keep going...


def main():
    """The sync subcommand handler.

    This method handles the 'sync' subcommand by forking off a daemon to watch
    a particular local repository and synchronize back to the remote.
    """
    # Load configuration
    configuration = get_configuration()

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

    # Figure out what we're going to call the repo directory.  We have to do
    # normpath call here because if remote_path contains a trailing /, the
    # basename will be empty.
    repo_directory_name = \
        ('remote'
         if remote_is_file
         else os.path.basename(os.path.normpath(remote_path)))
    repo_path = os.path.join(repo_container, repo_directory_name)

    # Clone the remote URL
    clone(clone_url, repo_path)

    # Set metadata on the local repo
    add_metadata_to_repo(repo_path, 'remoteIsFile', str(remote_is_file))
    add_metadata_to_repo(repo_path, 'remotePath', remote_path)
    add_metadata_to_repo(repo_path, 'cloneUrl', clone_url)

    # Print the repo path
    print(repo_path)

    # Daemonize
    daemonize()

    # We are the daemon!

    # Create a cleanup method
    def cleanup():
        # Do a push to the remote that'll cause it to self-destruct
        self_destruct_remote(repo_path)

        # Remove our own repository
        rmtree(repo_container)

    # We are the daemon!  Set up the signal handler for easy exit
    def signal_handler(signum, frame):
        # Cleanup and exit
        cleanup()
        exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    # Calculate our sync interval
    sync_interval = 10
    if configuration.has_option('core', 'syncInterval'):
        try:
            sync_interval = int(configuration.get('core', 'syncInterval'))
        except:
            # Just go with the default interval
            pass

    # Enter our main loop
    while True:
        # Do the sync
        sync_local_with_remote(repo_path)

        # Sleep
        time.sleep(sync_interval)

    # All done
    exit(0)
