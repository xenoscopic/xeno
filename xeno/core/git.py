# System imports
from sys import exit
from os.path import expanduser, exists, isfile, join, dirname, basename, \
    normpath, realpath, relpath
import subprocess
import uuid
from shutil import rmtree

# xeno imports
from .output import print_error
from .paths import get_working_directory


def _check_call(command_list, error_message, cwd=None, error_cleanup=None):
    """This method is a convenience wrapper for the Popen method, allowing one
    to call a subprocess and check its output, displaying an error message and
    exiting if the subprocess does not complete successfully.

    Args:
        command_list: The command and arguments to pass to Popen
        error_message: The message to print if there is an error.  It will be
            suffixed with the stdout/stderr of the subprocess.
        error_cleanup: A callable with no arguments that will be called on
            failure
    """
    # Start the subprocess
    p = subprocess.Popen(command_list,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,
                         cwd=cwd)

    # Wait for completion
    result = p.wait()

    # Check the result
    if result != 0:
        # If it's no good, print an error message
        print_error(error_message + ': ' + p.stdout.read())

        # Do the cleanup, if any
        if error_cleanup is not None:
            error_cleanup()

        # Bail
        exit(1)


def initialize_remote_repository(path):
    """This method initializes a remote repository which xeno can clone locally
    to do its editing.

    Args:
        path: The path of the file or directory that the repository should
            monitor and modify

    Returns:
        A string representing the repository path.
    """
    # Expand out the specified path
    path = realpath(normpath(expanduser(path)))

    # Validate it
    if not exists(path):
        print_error('Requested path does not exist: {0}'.format(path))
        exit(1)

    # Check what we're dealing with
    is_file = isfile(path)

    # Grab the xeno working directory.  Make sure it is real and normalized so
    # that we can check if the repository is a subdirectory of the work tree.
    xeno_working_directory = realpath(normpath(get_working_directory()))

    # Create a unique repository path.  We do not need to create the
    # repository - Git will do it for us.
    repo_path = join(xeno_working_directory, 'remote-' + uuid.uuid4().hex)

    # Figure out our working tree.  If we are editing a directory, it will be
    # the directory.  If we are editing a file, it will be the parent directory
    # and we will only include the file.
    work_path = dirname(path) if is_file else path

    # Do the initialization
    _check_call(['git',
                 '--work-tree',
                 work_path,
                 '--git-dir',
                 repo_path,
                 'init'],
                'Unable to initialize remote Git repository')

    # Create a cleanup in case anything fails
    error_cleanup = lambda: rmtree(repo_path)

    # Set up excludes
    with open(join(repo_path, 'info', 'exclude'), 'a') as exclude_file:
        # If this is a single file, exclude everything but the file
        if is_file:
            exclude_file.write('*\n')
            exclude_file.write('!{0}\n'.format(basename(path)))

        # If this is not a file, there are a few things to do
        if not is_file:
            # First, if the work tree is at a higher path than the repository,
            # add the repository as an exclude path
            relative_path = relpath(repo_path, work_path)
            if not relative_path.startswith('..'):
                exclude_file.write('{0}\n'.format(relative_path))

            # All the major SCM dirs to the exclude
            for scm_dir in ['.git', '.svn', '.hg']:
                exclude_file.write('{0}\n'.format(scm_dir))

    # Add all files and do the initial commit.  We have to use this wildcard
    # expression for the pathspec due to how git behaves when the work tree is
    # above the repo directory.  In any case, I think git will always ignore
    # the repo directory.
    _check_call(['git',
                 'add',
                 '-A',
                 join(work_path, '*')],
                'Unable to add initial files',
                cwd=repo_path,
                error_cleanup=error_cleanup)

    # Add all files and do the initial commit
    _check_call(['git',
                 'commit',
                 '--author',
                 '"xeno <xeno@xeno>"',
                 '-m',
                 '""',
                 '--allow-empty-message'],
                'Unable to commit initial files',
                cwd=repo_path,
                error_cleanup=error_cleanup)

    # Create an incoming branch
    _check_call(['git',
                 'branch',
                 'incoming'],
                'Unable to create incoming branch',
                cwd=repo_path,
                error_cleanup=error_cleanup)

    # TODO: Install hooks

    return repo_path


def clone(clone_url, local_destination):
    """Clones a remote URL to a local path, pulling down all branches and
    setting them up to track from the remote.

    This method will print an error and exit on failure.

    Args:
        clone_url: The repository URL
        local_destination: The local path to clone into.  It must not exist.
    """
    # Do the clone
    _check_call(['git',
                 'clone',
                 clone_url,
                 local_destination],
                'Unable to clone remote repository')


def add_metadata_to_repo(repo_path, key, value):
    """Sets the specified key to the specified value on the specified
    repository, adding it in the xeno section.

    This method will print an error and exit on failure.

    Args:
        repo_path: The path to the repository
        key: The key to set, must be camel case
        value: The value to set the key to
    """
    # Set the value
    _check_call(['git',
                 'config',
                 'xeno.{0}'.format(key),
                 value],
                'Unable to set repository metadata',
                cwd=repo_path)


def get_metadata_from_repo(repo_path, key):
    """Retrieve the metadata associated with the specified key in the specified
    repository under the xeno section.

    This method will print an error and exit on failure.  If the specified key
    doesn't exist, this method returns an empty string.

    Args:
        repo_path: The path to the repository
        key: The key to read, must be camel case

    Returns:
        The value associated with the key, if it exists, otherwise an empty
        string.  This method exits on failure.
    """
    try:
        output = subprocess.check_output(['git',
                                          'config',
                                          'xeno.{0}'.format(key)],
                                         cwd=repo_path)
    except:
        print_error('Unable to read repository metadata')
        exit(1)

    return output.strip()


def cloneable_remote_path(username, hostname, port, repo_path):
    """Constructs a cloneable Git URL capable of cloning the remote path.

    Args:
        username: The username to clone with or None
        hostname: The hostname to clone from
        port: The port to clone from or None
        repo_path: The path of the repository on the remote

    Returns:
        A string representing the cloneable path.
    """
    return 'ssh://{0}{1}{2}/{3}'.format(
        '{0}@'.format(username) if username else '',
        hostname,
        ':{0}'.format(port) if port else '',
        repo_path
    )
