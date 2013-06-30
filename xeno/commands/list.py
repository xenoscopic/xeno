# System imports
import sys
import os
import glob
import urlparse

# xeno imports
from ..core.paths import get_working_directory
from ..core.git import get_metadata_from_repo


def main():
    """The list subcommand handler.

    This method handles the 'list' subcommand by listing active xeno sessions.
    """
    # Get the xeno working directory
    working_directory = get_working_directory()

    # Grab all local repositories
    repo_paths = glob.glob(os.path.join(working_directory, 'local-*', '*'))

    # Loop through each one and print out the metadata
    for repo in repo_paths:
        # Grab the metadata
        process_id = get_metadata_from_repo(repo, 'syncProcessId')
        remote_path = get_metadata_from_repo(repo, 'remotePath')
        clone_url = get_metadata_from_repo(repo, 'cloneUrl')

        # Parse the URL
        clone_url = urlparse.urlparse(clone_url)

        # Check if the session is still alive
        # TODO: This is UNIX-specific
        try:
            pid = int(process_id)
            os.kill(pid, 0)
        except:
            continue

        print('{0}: {1} ({2}{3})'.format(
            process_id,
            remote_path,
            clone_url.username + '@' if clone_url.username else '',
            clone_url.hostname
        ))
