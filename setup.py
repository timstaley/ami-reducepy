#!/usr/bin/env python

from setuptools import setup


requirements = ['pexpect',
                'astropy>=0.4,<0.5'
]


setup(
    name="drive-ami",
    version="0.7.2",
    packages=['driveami'],
    scripts=['bin/driveami_filter_rawfile_listing.py',
             'bin/driveami_list_rawfiles.py',
             'bin/driveami_calibrate_rawfiles.py'],
    description="An interface layer for scripting the AMI-Reduce pipeline.",
    author="Tim Staley",
    author_email="timstaley337@gmail.com",
    url="https://github.com/timstaley/drive-ami",
    install_requires=requirements,
)
