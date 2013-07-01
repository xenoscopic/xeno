# System imports
import os
import sys
import argparse

# xeno imports
from xeno.core.git import commit


def parse_arguments():
    """Method to parse command line arguments.  In this case we do this to
    allow us to grab the path to the repository before passing it on to
    git-receive-pack.

    This function will parse command line arguments using the argparse module.

    Returns:
        A namespace of the arguments.
    """
    # Set up the core parser
    parser = argparse.ArgumentParser(add_help=False)

    # Add arguments
    parser.add_argument('repo_path',
                        action='store',
                        nargs='?')

    # Do the parsing of the arguments we want
    return parser.parse_known_args()[0]


def main():
    """The receive-pack subcommand handler.

    This method handles the 'xeno receive-pack' subcommand by first checking in
    any local changes on the master branch, then running the git-receive-pack
    command as normal.
    """
    # Parse command line arguments
    args = parse_arguments()

    # First do a commit on our local repository.  Since we're on the remote
    # end, we can commit deletions and creations.  If anybody adds anything, it
    # will be ignored by the excludes, and if anybody deletes the files, it'll
    # propagate to the remote end.
    if args.repo_path is not None:
        commit(args.repo_path, True, True, True)

    # Now just pass things through to the normal git-receive-pack (replacing
    # ourselves with git-receive-pack in the process)
    os.execvp('git-receive-pack', ['git-receive-pack'] + sys.argv[1:])
