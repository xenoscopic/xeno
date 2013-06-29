# Future imports to support fancy print() on Python 2.x
from __future__ import print_function

# System imports
import atexit
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

    # TODO: Parse out the username, hostname, and port from the SSH arguments

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

    # Now read our FIFO until it runs out, looking for xeno invocations
    while True:
        # Grab a new line
        line = fifo_file.readline()

        # Check if it is EOF (end of the process)
        if line == '':
            break

        # Check for our marker
        clean_line = line.strip()
        if clean_line == 'hello world':
            # Suspend SSH
            ssh.send_signal(signal.SIGSTOP)

            # Launch our editor
            run_editor_on_local_path('/Users/jacob/Projects/owls',
                                        exit_on_no_editor=False)
            
            # Resume SSH
            ssh.send_signal(signal.SIGCONT)

    # Close the FIFO.  It'll be removed from disk automatically at exit
    fifo_file.close()

    # Wait for SSH to finish (it should have already) and exit with its return
    # code
    print('bailing')
    exit(ssh.wait())
