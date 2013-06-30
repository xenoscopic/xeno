# Setuptools imports
from setuptools import setup, find_packages


# Setup the xeno utilities
setup(
    # Basic installation information
    name='xeno',
    version='0.0.1',
    packages=find_packages(exclude=['testing']),
    package_data={
        'xeno': ['hooks/post-receive']
    },
    entry_points={
        'console_scripts': [
            'xeno = xeno.xeno.commands.main:main',
            'xeno-config = xeno.xeno.commands.config:main',
            'xeno-edit = xeno.xeno.commands.edit:main',
            'xeno-ssh = xeno.xeno.commands.ssh:main',
            'xeno-sync = xeno.xeno.commands.sync:main',
            'xeno-list = xeno.xeno.commands.list:main',
            'xeno-resume = xeno.xeno.commands.resume:main',
            'xeno-stop = xeno.xeno.commands.stop:main',

            # Convenience aliases for users to use as a replacement for their
            # normal editor command
            'xen = xeno.xeno.commands.edit:main'
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
