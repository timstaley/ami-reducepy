#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="drive-ami",
    version="0.3.1",
    packages=['driveami'],
    description="A python package for scripting the AMI-reduce pipeline.",
    author="Tim Staley",
    author_email="timstaley337@gmail.com",
    url="https://github.com/timstaley/drive-ami",
    install_requires=required,
)
