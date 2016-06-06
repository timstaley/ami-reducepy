============
drive-ami
============
A python package for scripting the AMI_-reduce pipeline.

For a full description, see `Staley and Anderson (2015)`_. 
If you use drive-ami in work leading to a publication, we ask that you cite 
the paper above, and the relevant `ASCL entry`_.

.. _AMI: http://www.mrao.cam.ac.uk/telescopes/ami/
.. _Staley and Anderson (2015): https://github.com/timstaley/automated-radio-imaging-paper
.. _ASCL entry: http://ascl.net/1502.017


Rationale
---------
From a radio astronomy point of view:
 This package makes it trivial to script reduction of raw AMI data
 from python. What's more, it provides tools to group the raw files into 
 datasets, outputting the UVFITS for each dataset under a single folder.
 It does this by extracting the pointing information from the raw data,
 resulting in fairly reliable groupings (although you can edit these manually, 
 see later). 

 When processing the data, all output from ``reduce`` is saved to an
 accompanying log-file, retaining all information that would normally 
 be available to the user from the interactive interface.
 Meanwhile, all emulated commands passed to ``reduce`` are 
 recorded in a separate log for each file processed, so it's easy to
 re-run the script manually and tinker with the reduction process.
 
 Additionally, when running commands listed in a script the interface
 quietly parses key information such as flagging percentages, 
 rain modulation, and estimated noise, from the ``reduce`` output. 
 These are then stored to disk alongside the UVFITs in easily 
 machine readable JSON format. 
 (These may also be added to the UVFITS header in future.)

 

From a software engineering point of view:
 Written in Fortran, with an interactive terminal interface, the ``reduce`` 
 pipeline takes a little coaxing to co-operate with calling scripts, 
 making automated processing of large numbers of files tricky.
 Fortunately, the python library ``pexpect`` provides an easy mechanism 
 to emulate human interaction, upon which I've built an interface class.
 Limitations such as a maximum path length of ~32 chars are circumvented
 with a few careful hacks. 
 The python logging libraries then allow us provide the user with 
 minimal progress information, whilst retaining all possible information 
 for debugging and scientific evaluation.
 
Installation
------------

*Requirements*:
 - You will need a working installation of AMI-reduce (naturally)
 - `pexpect <http://pypi.python.org/pypi/pexpect/>`_ For interfacing with AMI-reduce.
   (Installed automatically as part of the python setup.) 
 - `astropy <http://astropy.org/>`_ Used for calculating
   co-ordinate distances, etc.
   (Installed automatically as part of the python setup.)
   
From the command line (preferably within a virtualenv):: 

 git clone git://github.com/timstaley/drive-ami.git
 cd drive-ami
 pip install numpy #Workaround for buggy scipy/numpy combined install.
 pip install .

Usage
-----

Command-line scripts are installed along with the package. 
Their sourcefiles can be found at https://github.com/timstaley/drive-ami/tree/master/bin.
For full details, run e.g.::

    driveami_list_rawfiles.py -h

Where ``-h`` is short for 'help'.

Typical usage is to run ``driveami_list_rawfiles.py`` to build a full
listing of available data, followed by ``driveami_filter_rawfile_listing.py`` 
to extract the entries on a desired target. 
Finally, ``driveami_calibrate_rawfiles.py`` actually does the processing using 
AMI-REDUCE.


