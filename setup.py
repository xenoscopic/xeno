# Setuptools imports
from setuptools import setup, find_packages


# Setup the xeno utilities
setup(
    # Basic installation information
    name='xeno',
    version='0.0.4',
    packages=find_packages(exclude=['testing']),
    package_data={
        'xeno': ['hooks/post-receive']
    },
    entry_points={
        'console_scripts': [
            'xeno = xeno.commands.main:main',
            'xeno-config = xeno.commands.config:main',
            'xeno-edit = xeno.commands.edit:main',
            'xeno-ssh = xeno.commands.ssh:main',
            'xeno-sync = xeno.commands.sync:main',
            'xeno-list = xeno.commands.list:main',
            'xeno-resume = xeno.commands.resume:main',
            'xeno-stop = xeno.commands.stop:main',

            # Convenience aliases for users to use as a replacement for their
            # normal editor command
            'xen = xeno.commands.edit:main',

            # Special wrapper for git-receive-pack which will do a check for
            # and commit of changes on the remote any time there is a push,
            # regardless of whether that push actually sends any commits to the
            # remote
            'xeno-receive-pack = xeno.commands.receive:main'
        ],
    },

    # Metadata for PyPI
    author='Jacob Howard',
    author_email='jacob@havoc.io',
    description='Synchronous remote file editing with SSH and Git',
    license='MIT',
    keywords='remote file folder editing ssh git',
    url='https://xeno.io'
)
