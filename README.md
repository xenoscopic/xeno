xeno
====

xeno allows you to edit files and folders on a remote computer using the editor
on your local machine.  It synchronizes data using Git and SSH, making it robust
to connection dropouts and easily allowing you to work offline.  Best of all, it
runs entirely in user-space, so you can set it up and use it without complicated
kernel modules or administrative privileges.


Features and basic usage
------------------------

To start editing a remote path over SSH, use:

    xeno edit user@hostname:/the/path

xeno will clone the remote path locally and keep it in sync with the remote
copy, or, if you are already in an SSH session<sup>1</sup>, you can do:

    xeno edit /the/path

and it will have exactly the same effect!

<sup>
1: For in-session launches, you must use `xeno ssh`, a VERY thin wrapper around
SSH which monitors console output for initialization messages
([FAQ](https://github.com/havoc-io/xeno/wiki/FAQs#isnt-it-insecure-to-use-the-xeno-ssh-wrapper)).
</sup>


Extended usage
--------------

To view help information, use

    xeno --help

xeno uses a variety of subcommands to do its bidding (e.g. `config`, `edit`,
...).  To view help information for a particular subcommand, use:

    xeno SUBCOMMAND_NAME --help

xeno supports the following subcommands:

- [__edit__](https://github.com/havoc-io/xeno/wiki/edit): Starts editing sessions
- [__config__](https://github.com/havoc-io/xeno/wiki/config): Manages xeno configuration information
- __ssh__: A pass-through to 'ssh' which monitors console output for session initialization
  ([see FAQ](https://github.com/havoc-io/xeno/wiki/FAQs#isnt-it-insecure-to-use-the-xeno-ssh-wrapper)).
- [__list__](https://github.com/havoc-io/xeno/wiki/list): Lists active xeno sessions
- [__resume__](https://github.com/havoc-io/xeno/wiki/resume): Resumes a xeno session (open your editor on the local copy)
- [__stop__](https://github.com/havoc-io/xeno/wiki/stop): Stops a xeno session and cleans up local/remote resources
- [__sync__](https://github.com/havoc-io/xeno/wiki/sync): Manually syncs a xeno session with the remote copy
- [__daemon__](https://github.com/havoc-io/xeno/wiki/sync): Starts and stops the xeno daemon

To keep consistency, if you use the `xeno edit` command on a local path, it will
simply open the local path in your editor.  Thus, it is often convenient to
alias the `xeno edit` command as something like `xen`, and use the `xen` command
as a way to consistently launch your editor, both locally and remote.


Requirements
------------

xeno has a *very* minimal set of system dependencies, in particular:

- A POSIX-compliant operating system and shell
- OpenSSH
- OpenSSL
- Git

Most systems meet the POSIX, OpenSSH, and OpenSSL requirements out of the box,
and Git is generally going to be installed on most systems of interest.  These
requirements apply to both ends of the editing connection, though on the client
side only OpenSSH client is required, and on the server side only OpenSSH server
is required.

If there are issues, please let me know.  I'd like to make things work on as
many systems and shells as possible (within reason).


Installation
------------

The xeno program is a portable shell script, so you can simply download it from
here and put it somewhere in your path.

xeno needs to be installed on both ends of the editing connection.  You also
need to have the installation directory in your path for both login __AND__
non-login shells.  For Bash-like shells, this generally means an entry in
`~/.bash_profile` or `~/.profile` (for login shells) and `~/.bashrc` (for
non-login shells).  For Zsh-like shells, this generally means an entry in
`~/.zshenv` (for both login and non-login shells).  Consult your shell's
documentation for more information.

You also need to launch the xeno daemon on the local end if you want automatic
synchronization (you do not need to run the daemon on the remote end). This can
be accomplished using the `xeno daemon` command.  This command will not start
another daemon if one is already running, so it is advised that you simply put
this into your login shell initialization script.

It is important to note that on some systems, e.g. Ubuntu, there is a statement
in the default ~/.bashrc to prevent it from being run for non-interactive
shells, so you either need to remove this statement or add the path statement
before that. It typically looks something like:

    # If not running interactively, don't do anything
    case $- in
        *i*) ;;
        *) return;;
    esac

Also, if you want in-session launch capabilities, you need to do:

    alias ssh="xeno ssh"

The `xeno ssh` command is just a pass-through to SSH, but it monitors SSH's
console output for initialization tokens.  If this is a little too
tin-foil-hat-inducing for you, you can still use the local launch mechanism
without losing any sleep.  For more information, please see the
[FAQ](https://github.com/havoc-io/xeno/wiki/FAQs#isnt-it-insecure-to-use-the-xeno-ssh-wrapper)
on this topic.


Configuration
-------------

xeno's configuration is managed via the 'xeno config' command.  To print the
current configuration, use:

    xeno config

Configuration values can be set with:

    xeno config key value

Configuration values can be viewed with:

    xeno config key

Configuration values can be cleared with:

    xeno config key --clear

xeno supports the following configuration keys:

- __core.editor__: The editor command to use.  If not set, xeno will fall back
  to the EDITOR environment variable.
- __sync.interval__: The period, in seconds, for the daemon to wait between
  checks for local changes.  The default is 10.
- __sync.force__: By default, the daemon only checks for changes on the remote
  when pushing local changes.  If this is set to True, xeno will check the
  remote for changes every time it checks the local copy.


Implementation
--------------
The best way to understand xeno's implementation is to simply read it.  It's
only about 1,200 lines of shell script, which is organized roughly as:

    # Constants
    # Initialization
    # Utility functions
    # Individual command implementations
    # Main entry/command-dispatch point

When xeno is invoked, it will generate an out-of-work-tree Git repository on the
remote machine to track and coordinate changes.  It installs some hooks in the
remote repository to do some comitting/merging on the remote end every time a
push is received from the local end.  xeno will then clone the remote
repositor and launch your local editor on the clone.  The basic repository
synchronization flow looks like:   

    ------------------------------------------------------------------------
    |                                                               Editor |
    ------------------------------------------------------------------------
                                      |
                                      |
    ----------------------------------|-------------------------------------
    |                                 |                   Local Repository |
    |                                \|/       (non-bare, edited directly) |
    |                              <master>                                |
    |                               |   /|\                                |
    --------------------------------|----|----------------------------------
                                    |    |
     1: Local changes are committed |    | 3. Remote changes are pulled
        and pushed to the remote's  |    |    back to the local working
        incoming branch             |    |    copy, keeping the local copy
                                    |    |    as canonical with '-X ours'
                                    |    |
    --------------------------------|----|----------------------------------
    |                               |    |               Remote Repository |
    |                              \|/   |        (bare, out-of-work-tree) |
    |                       <incoming>   |                                 |
    |                               |    |                                 |
    | 2. pre/post-receive hooks     |    |                                 |
    |    commit the remote master   |    |                                 |
    |    and merge the incoming     |    |                                 |
    |    changes into master,       |    |                                 |
    |    keeping the incoming       |    |                                 |
    |    changes as canonical with  |    |                                 |
    |    '-X theirs'                |    |                                 |
    |                               |    |                                 |
    |                              <master>                                |
    ----------------------------------|-------------------------------------
                                      |
                                     \|/
    ------------------------------------------------------------------------
    |                                                          Remote Path |
    ------------------------------------------------------------------------

Because the remote Git repository is outside of the work tree, you can use it to
edit remote folders which may already be Git repositories without any conflicts.
xeno also works for editing single remote files.  Best of all, because it uses
Git, it will safely merge changes to and from the remote, and if your local
editor is Git-aware, it will show you which files have or haven't been synced to
the remote.

xeno provides a variety of commands for starting, managing, resuming, and ending
sessions.  xeno is robust, and the daemon will continue trying to sync changes
to the remote repository even if SSH access becomes temporarily unavailable.
When the editing session is ended, xeno will automatically clean up all local
and remote resources.


More Information
----------------
For more detailed information, please see the
[xeno wiki](https://github.com/havoc-io/xeno/wiki) and
[FAQs](https://github.com/havoc-io/xeno/wiki/FAQs).


TODO
----
- Implement Travis CI testing
