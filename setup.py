#!/usr/bin/env python

from setuptools import setup

try:
    with open('requirements.txt', 'r') as f:
        requirements = f.read().split()
except IOError:
    with open('robot_zoo.egg-info/requires.txt', 'r') as f:
        requirements = f.read().split()

setup(name='robot_zoo',
      author='Joost Molenaar',
      author_email='j.j.molenaar@gmail.com',
      version_command=('git describe', 'pep440-git-full'),
      packages=['robot_zoo', 'robot_zoo.bot'],
      install_requires=requirements)
