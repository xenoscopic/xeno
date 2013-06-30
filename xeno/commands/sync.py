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
from xeno.core.output import print_error
from xeno.core.configuration import get_configuration, string_to_bool
from xeno.core.paths import get_working_directory
from xeno.core.git import clone, add_metadata_to_repo, \
    sync_local_with_remote, self_destruct_remote


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
    parser.add_argument('--no-daemon',
                        action='store_true',
                        help='do not daemonize (for debugging)',
                        dest='no_daemon')

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

    # Do the second fork
    if os.fork() > 0:
        # This is the intermediate, exit calmly
        # Recommended exit method on fork()
        os._exit(0)

    # Otherwise, we're in the second child, set our outputs and keep going...
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')


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
        os.makedirs(repo_container, 0o700)
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

    # Print the editable path.
    # HACK: We have to flush, because the daemon process will inherit the same
    # file descriptors and since they are never closed, this line may remain
    # buffered indefinitely, causing anyone waiting for the output to wait
    # for-ev-er.
    if remote_is_file:
        print(os.path.join(repo_path, os.path.basename(remote_path)))
    else:
        print(repo_path)
    sys.stdout.flush()

    # Daemonize (unless told not to)
    if not args.no_daemon:
        daemonize()

    # We are the daemon (or the original process if we didn't daemonize).  Add
    # our process id to the remote metadata
    add_metadata_to_repo(repo_path, 'syncProcessId', str(os.getpid()))

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
    signal.signal(signal.SIGTERM, signal_handler)

    # Calculate our sync interval
    sync_interval = 10
    if configuration.has_option('sync', 'syncInterval'):
        try:
            sync_interval = int(configuration.get('sync', 'syncInterval'))
        except:
            # Just go with the default interval
            pass

    # Calculate whether or not to poll the remote
    poll_remote = False
    if configuration.has_option('sync', 'pollForRemoteChanges'):
        try:
            poll_remote = string_to_bool(
                configuration.get('sync', 'pollForRemoteChanges')
            )
        except:
            # Invalid value...
            pass

    # Enter our main loop
    succeeded_last_time = True
    while True:
        # Do the sync
        succeeded_last_time = \
            sync_local_with_remote(repo_path,
                                   poll_remote,
                                   remote_is_file,
                                   not succeeded_last_time)

        # Sleep
        time.sleep(sync_interval)

    # All done (unreachable code, but whatever)
    exit(0)
