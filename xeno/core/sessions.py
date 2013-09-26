# System imports
import os
import glob
from itertools import chain

# xeno imports
from xeno.core.output import print_error
from xeno.core.paths import get_working_directory
from xeno.core.git import get_metadata_from_repo, status
from xeno.core.configuration import string_to_bool


# Session metadata keys
XENO_SESSION_LOCAL_PROCESS_ID = 'syncProcessId'
XENO_SESSION_LOCAL_REPOSITORY_PATH = 'repositoryPath'
XENO_SESSION_REMOTE_CLONE_URL = 'cloneUrl'
XENO_SESSION_REMOTE_PATH = 'remotePath'
XENO_SESSION_REMOTE_IS_FILE = 'remoteIsFile'
XENO_SESSION_SYNC_STATUS = 'syncStatus'


def get_sessions():
    """Gets a list of active xeno sessions.

    Returns:
        A list of dictionaries, each with the keys defined in xeno.sessions:

            XENO_SESSION_LOCAL_PROCESS_ID: The local sync daemon process id
            XENO_SESSION_LOCAL_REPOSITORY_PATH: The local repository path
            XENO_SESSION_REMOTE_CLONE_URL: The URL used to clone the remote
            XENO_SESSION_REMOTE_PATH: The remote path
            XENO_SESSION_REMOTE_IS_FILE: Whether or not the remote target is a
                a file
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
        clone_url = get_metadata_from_repo(repo, 'remote.origin.url', True)
        remote_is_file = string_to_bool(get_metadata_from_repo(
            repo,
            'remoteIsFile'
        ))

        # Check if the session is still alive
        # TODO: This is UNIX-specific
        try:
            os.kill(process_id, 0)
        except:
            print_error('Dead sync process id: {0} in {1}'.format(
                process_id,
                repo
            ))
            continue

        # Check the sync status
        changes = list(chain(*status(repo)))
        sync_status = 'unsynced' if changes else 'synced'

        # Add the result
        results.append({
            XENO_SESSION_LOCAL_PROCESS_ID: process_id,
            XENO_SESSION_LOCAL_REPOSITORY_PATH: repo,
            XENO_SESSION_REMOTE_CLONE_URL: clone_url,
            XENO_SESSION_REMOTE_PATH: remote_path,
            XENO_SESSION_REMOTE_IS_FILE: remote_is_file,
            XENO_SESSION_SYNC_STATUS: sync_status
        })

    return results
