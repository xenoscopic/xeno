# System imports
import os
import glob
try:
    # Python 2.x
    from urlparse import urlparse
except ImportError:
    # Python 3.x
    from urllib.parse import urlparse

# xeno imports
from xeno.core.output import print_error
from xeno.core.paths import get_working_directory
from xeno.core.git import get_metadata_from_repo


def get_sessions():
    """Gets a list of active xeno sessions.

    Returns:
        A list of tuples, each of the form:

            (process_id, remote_path, username, hostname)
    """
    # Get the xeno working directory
    working_directory = get_working_directory()

    # Grab all local repositories
    repo_paths = glob.glob(os.path.join(working_directory, 'local-*', '*'))

    # Create results
    results = []

    # Loop through each repository path and print out the metadata
    for repo in repo_paths:
        # Grab the metadata
        process_id = get_metadata_from_repo(repo, 'syncProcessId')
        try:
            process_id = int(process_id)
        except:
            print_error('Invalid sync process id: {0} in {1}'.format(
                process_id,
                repo
            ))
            continue
        remote_path = get_metadata_from_repo(repo, 'remotePath')
        clone_url = get_metadata_from_repo(repo, 'cloneUrl')

        # Parse the URL
        clone_url = urlparse(clone_url)

        # Check if the session is still alive
        # TODO: This is UNIX-specific
        try:
            os.kill(process_id, 0)
        except:
            continue

        # Add the result
        results.append((
            process_id,
            remote_path,
            clone_url.username + '@' if clone_url.username else None,
            clone_url.hostname
        ))

    return results
