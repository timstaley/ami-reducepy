============
ami-reducepy
============
A python package for scripting the AMI_-reduce pipeline.

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
 - `astropysics <http://packages.python.org/Astropysics/>`_ Used for calculating
   co-ordinate distances, etc.
   (Installed automatically as part of the python setup.)
   
From the command line (preferably within a virtualenv):: 

 git clone git://github.com/timstaley/ami-reducepy.git
 cd ami-reducepy
 pip install .

Usage
-----
The class ``ami.Reduce`` provides an easily scriptable interface to the ``reduce`` pipeline.
At this stage I haven't documented it, but in the meantime you can get started 
with the example scripts described below. 
(Of course at <500 lines, the source code is pretty easy to dive into and get aquainted with).

First try ``./list_ami_datasets.py --help`` to see your options. 
Unless you edit the defaults in the script, or happen to have an ami installation 
under */opt/ami*, then you will probably want to run::

 ./list_ami_datasets.py --ami-dir=/path/to/ami

By default, this will output a JSON file listing dataset groupings, 
to *datasets.json*.
This file has a very simple structure - the first element is a string 
representing the array type ('LA' or 'SA'), 
and after that comes a nested dictionary representing the dataset file groups.
You should copy this file to e.g. *files_to_process.json* and then 
edit the nested dictionaries to leave just the files you wish to process.
Note that the key to each top-level dictionary entry represents the group name - 
by default this is guessed from the file names, 
but you can change it to whatever you like.
`Be careful to match your brackets and mind your commas!`

Now you have a target list, try ``./process_ami_data.py --help``.
After a careful inspection, you'll probably want to try something like::

 ./process_ami_data.py --ami-dir=/path/to/ami  files_to_process.json

While that's churning, you can follow the newly created file *ami-reduce.log* to get the full input / output stream being passed to ``reduce``, with some additional comments here and there. Per-file logs will also be created alongside the output UVFITS files.

To Do:
------
- Output full listings along with dataset groupings.


.. _AMI: http://www.mrao.cam.ac.uk/telescopes/ami/
