# Future imports to support fancy print() on Python 2.x
from __future__ import print_function

# System imports
import sys
import subprocess


def check_for_xeno_edit_initialization(line):
    """Checks the given line for an initialization of xeno, and if it finds
    one, starts a xeno session.

    Arg:
        line: The line to Check
    """
    pass


def main():
    """The ssh subcommand handler.

    This method handles the 'ssh' subcommand by starting an ssh session which
    is xeno-aware.
    """
    # Create an SSH process
    ssh = subprocess.Popen(['ssh'] + sys.argv[1:],
                           stdout=subprocess.PIPE)

    # While it is still running, grab the output and write it
    # character-by-character to our own STDOUT, watching for xeno
    # initializations
    current_line = ''
    while ssh.poll() is None:
        # Grab the next character
        c = ssh.stdout.read(1)

        # Check if we hit a newline character
        if c in '\n\r':
            # We are starting a new line
            check_for_xeno_edit_initialization(current_line)

            # Clear the current line
            current_line = ''
        else:
            current_line += c

        # Print the character
        print(c, end='')

    # All done
    exit(0)
