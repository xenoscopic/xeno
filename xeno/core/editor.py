# System imports
import os
from sys import exit
import subprocess

# xeno imports
from .output import print_error
from .configuration import load_configuration


def launch_editor_on_local_path(local_path, replace=False):
    """Launches the user's editor on the specified local path.

    If no editor can be identified from xeno settings or the EDITOR environment
    variables, prints an error and exits.

    Args:
        local_path: A string representing the local path to open.
        replace: Whether or not to replace the current process with the editor

    Returns:
        If replace is True, this method does not return.  If replace is false,
        returns a subprocess.Popen object representing the editor.
    """
    # Load configuration
    configuration = load_configuration()

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
        exit(1)

    # Launch the editor in the manner requested
    if replace:
        os.execvp(editor, [editor, local_path])
    else:
        return subprocess.Popen([editor, local_path])
