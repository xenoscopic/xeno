# System imports
import os
from sys import exit

# xeno imports
from .output import print_error
from .configuration import load_configuration


def launch_editor_on_local_path(local_path):
    """Launches the user's editor on the specified local path, replacing the
    current executable.

    If no editor can be identified from xeno settings or the EDITOR environment
    variables, prints an error and exits.

    Args:
        local_path: A string representing the local path to open.

    Returns:
        This method does not return.
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

    # Launch the editor, replacing the current process
    os.execvp(editor, [editor, local_path])
