# Use the distribute version of setuptools
from distribute_setup import use_setuptools
use_setuptools()

# Setuptools imports
from setuptools import setup


# Setup the xeno utilities
setup(
    # Basic installation information
    name='xeno',
    version='0.0.1',
    packages=['xeno'],
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
            'xen = xeno.commands.edit:main'
        ],
    },
    install_requires=['watchdog>=0.6.0'],

    # Metadata for PyPI
    author='Jacob Howard',
    author_email='jacob@havoc.io',
    description='Synchronous remote file editing with SSH and Git',
    license='MIT',
    keywords='remote file folder editing ssh git',
    url='https://xeno.io'
)
