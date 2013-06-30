# System imports
import os
import subprocess
from sys import exit

# xeno imports
from xeno.core.output import print_error
from xeno.core.configuration import get_configuration


def run_editor_on_local_path(local_path, exit_on_no_editor=True):
    """Launches the user's editor on the specified local path and waits for it
    to complete.

    If no editor can be identified from xeno settings or the EDITOR environment
    variables, prints an error and exits.

    Args:
        local_path: A string representing the local path to open.
        exit_on_no_editor: Whether or not to exit if the editor cannot be
            determined

    Returns:
        The exit status code of the editor, or if no editor could be
        identified and exit_on_no_editor=False, returns None.
    """
    # Load configuration
    configuration = get_configuration()

    # Check if the user has specified an editor
    editor = None
    if configuration.has_option('core', 'editor'):
        editor = configuration.get('core', 'editor')

    # Check if we need to fall-back to the EDITOR environment variable
    if editor is None:
        editor = os.environ.get('EDITOR', None)

    # If we still haven't identified an editor, bail
    if editor is None:
        print_error('Unable to identify editor.  Either set the xeno '
                    '\'core.editor\' option or the \'EDITOR\' environment '
                    'variable.')
        if exit_on_no_editor:
            exit(1)
        else:
            return None

    # Launch the editor and wait for it to finish
    return subprocess.call([editor, local_path])
