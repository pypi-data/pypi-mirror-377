#!/usr/bin/env python

__version__ = '0.0.7'

import sys
import os
from setuptools import setup  # , find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='SetupVariableTracker',
      version=__version__,
      use_2to3=False,
      author='Rene Vollmer',
      author_email='admin@aypac.de',
      maintainer='Rene Vollmer',
      maintainer_email='admin@aypac.de',
      description='Small library to track and log the declaration of new (setup) variables',
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      url='https://github.com/Aypac/SetupVariableTracker',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Scientific/Engineering',
      ],
      python_requires='>=3.6',
      # license=read('LICENCE'),
      # if we want to install without tests:
      # packages=find_packages(exclude=["*.tests", "tests"]),
      # packages=find_packages(),
      packages=["SetupVariableTracker", ],
      provides=["SetupVariableTracker"],
      package_dir={"SetupVariableTracker": "SetupVariableTracker"},
      install_requires=['tabulate', ],
      #test_suite='SetupVariableTracker.tests',
      zip_safe=False,
      )
