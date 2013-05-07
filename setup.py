#!/usr/bin/env python

from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="ami-reducepy",
    version="0.1.1",
    packages=['ami'],
    description="A python package for scripting the AMI-reduce pipeline.",
    author="Tim Staley",
    author_email="timstaley337@gmail.com",
    url="https://github.com/timstaley/ami-reducepy",
    install_requires=required,
)
