#!/usr/bin/env python2.7

from setuptools import setup

try:
    with open('requirements.txt', 'r') as f:
        requirements = f.read().split()
except IOError:
    with open('twitter.egg-info/requires.txt', 'r') as f:
        requirements = f.read().split()

setup(name='twitter',
      author='Joost Molenaar',
      author_email='j.j.molenaar@gmail.com',
      version_command='git describe',
      packages=['robot_zoo', 'robot_zoo.bot'],
      data_files=[ ('bin', ['bin/mail-log']) ],
      install_requires=requirements)
