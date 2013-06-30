# System imports
import subprocess
from cStringIO import StringIO

# xeno imports
from xeno.core.output import print_error


def start_syncing(remote_path_is_file, remote_path, cloneable_path):
    """Starts the xeno-sync command on the specified location, returning the
    local editing path once the sync daemon has started.

    This method prints an error if it fails, but does not exit.

    Args:
        remote_path_is_file: Whether or not the remote path is a file
        remote_path: The path on the remote
        cloneable_path: The clone URL for the remote repository

    Returns:
        The locally-cloned repository path to pass to the editor, or None if
        the daemon could not be started.
    """
    # Launch the xeno-sync command
    command = ['xeno-sync',
               '--remote-path',
               remote_path,
               '--clone-url',
               cloneable_path]
    if remote_path_is_file:
        command.append('--file')
    try:
        # HACK: Use Popen because check_output seems to halt waiting for all
        # child processes to complete, even though the daemon forked off of
        # the child process and has a parent id of init.  No clue why.  If we
        # call wait here, it seems to go fine
        xeno_sync = subprocess.Popen(command,
                                     stdout=subprocess.PIPE)
        xeno_sync.wait()

        # Grab the output
        return xeno_sync.stdout.readline().strip()
    except:
        print_error('Unable to start synchronization daemon')
        return None
