xeno
====

xeno allows you to edit files and folders on a remote computer using the editor
on your local machine.  It synchronizes data using Git and SSH, making it
robust to connection dropouts and even allowing you to work offline.  Best of
all, it runs entirely in user-space, so you can set it up and use it without
complicated kernel modules or administrative privileges.


Features and basic usage
------------------------

TODO: Write


Extended usage
--------------

TODO: Write


Requirements
------------

xeno has a *very* minimal set of system dependencies, in particular:

- A POSIX-compliant operating system and shell
- OpenSSH
- Git

Most systems meet the POSIX and OpenSSH requirements out of the box, and Git is
generally going to be installed on most systems of interest.  These requirements
apply to both ends of the editing connection, though on the client side only
OpenSSH client is required, and on the server side only OpenSSH server is
required.

If there are issues, please let me know.  I'd like to make things work on as
many systems as possible.


Installation
------------

TODO: Write


Configuration
-------------

TODO: Write


Implementation
--------------

TODO: Write
