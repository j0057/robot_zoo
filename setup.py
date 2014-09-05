#!/usr/bin/env python2.7

from setuptools import setup

setup(name='twitter',
      author='Joost Molenaar',
      author_email='j.j.molenaar@gmail.com',
      version_command='git describe',
      packages=['robot_zoo'],
      data_files=[ ('bin', 'bin/mail-log') ])
