xeno
====
xeno is a command-line based synchronous remote file editing system which uses
SSH and Git to add remote editing capabilities to your text editor of choice.


Features
--------
xeno allows you to remotely edit files over SSH so that you can use that fancy
$70 GUI text editor you bought instead of having to drop into vim everytime you
"go abroad" to edit files.  Or if you are a diehard vim/emacs user, you can save
yourself time by editing without lag and not having to port your configuration
to every server you work on.


Requirements
------------
- Python 2.7+
- Git
- OpenSSH


Installation
------------



Usage
-----
To view help information, use

    xeno --help

xeno uses a variet of subcommands to do its bidding (e.g. config, edit, ...).
To view help information for a particular subcommand, use:

    xeno YOUR_SUBCOMMAND --help

By default, xeno will launch whatever editor is specified in the EDITOR
environment variable.  You can override this by setting an editor for xeno to
use:

    xeno config core.editor YOUR_EDITOR_COMMAND

You can see if any editor has been set to override $EDITOR with the following:

    xeno config core.editor

If you want to clear the setting, use

    xeno config --clear core.editor

The 'config' subcommand follows the usage pattern described above for all
configuration values, not just 'core.editor'.  The list of settings currently
recognized by xeno include:

- core.editor
- core.workingDirectory
- sync.syncInterval
- sync.pollForRemoteChanges

To start editing a path, use

    xeno edit [path]

A path can be composed as follows:

    [[user@]hostname[:PORT]:]FILE_PATH

If a local path is provided (with no remote username/hostname/port) then xeno
will simply launch your editor on the local path.  


Internals
---------


