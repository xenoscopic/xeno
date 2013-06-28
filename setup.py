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
    entry_points={
        'console_scripts': [
            'xeno = xeno.commands.main:main',
            'xeno-config = xeno.commands.config:main',
            'xeno-edit = xeno.commands.edit:main'
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
