#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from setuptools import find_packages, setup, Command
from shutil import rmtree


NAME = 'daily_digest'
DESCRIPTION = 'Simple daily summary email with charts.'
URL = 'https://github.com/nickromano/django-daily-digest'
EMAIL = 'nick.r.romano@gmail.com'
AUTHOR = 'Nick Romano'

here = os.path.abspath(os.path.dirname(__file__))

about = {}
with open(os.path.join(here, NAME, '__init__.py')) as f:
    exec(f.read(), about)


class PublishCommand(Command):
    """Support setup.py publish."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Print things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.sep.join(('.', 'dist')))
        except FileNotFoundError:  # noqa
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        os.system('twine upload dist/*')

        sys.exit()


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    license='MIT',
    package_data={'daily_digest': ['templates/daily_digest/*.html']},
    install_requires=[
        'Django>=1.8',
        'CairoSVG>=2.0.3',
        'premailer',
    ],
    # Dependency links are no longer supported by pip so the leather code has been copied to this repo
    # until this PR is merged: https://github.com/wireservice/leather/pull/89.
    # dependency_links=[
    #     'git+ssh://git@github.com/nickromano/leather.git#egg=leather-0.3.3',
    # ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    tests_require=[
        'mock'
    ],
    test_suite='testrunner.runtests',
    cmdclass={
        'publish': PublishCommand
    },
)
