#!/usr/bin/env python

from setuptools import setup
import versioneer

requirements = ['pexpect>=4.0.1,<5',
                'astropy>=1.0,<2',
                'colorlog',
]


setup(
    name="drive-ami",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
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
