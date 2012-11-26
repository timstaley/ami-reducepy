===============
ami-reduce
===============
A python package for scripting the AMI-reduce pipeline.

Rationale
-----------
From a radio astronomy point of view:
 This package makes it trivial to script reduction of raw AMI data
 from python. What's more, it provides tools to group the raw files into 
 datasets, outputting the UVFITS for each dataset under a single folder.
 It does this by extracting the pointing information from the raw data,
 resulting in fairly reliable groupings (although you can edit these manually, 
 see later). 

 When processing the data, all output from ``reduce`` is saved to an
 accompanying log-file, retaining all information that would normally 
 be made available.
 Finally, all emulated commands passed to ``reduce`` are 
 recorded in a separate log for each file processed, so it's easy to
 re-run the script manually and tinker  with the reduction process.

From a software engineering point of view:
 ``reduce`` is a textbook example of legacy scientific software - 
 well used, it has performed reliably for years and is still producing
 valuable scientific data. 
 However, the software was not designed with large 
 automated batch processing in mind (which is now commonplace, 
 given vastly increased computational resources). 
 Written in fortran, with an interactive terminal interface, the pipeline takes a 
 little coaxing to co-operate with calling scripts.
 Fortunately, the python library
 ``pexpect`` provides an easy mechanism to emulate human interaction. 
 Limitations such as a maximum path length of ~32 chars are also circumvented
 with a few careful hacks.
 
Requirements
-----------------
 - A working installation of AMI-reduce (naturally)
 - `pexpect <http://pypi.python.org/pypi/pexpect/>`_ (Install with e.g ``sudo apt-get install python-pexpect``)
 - `astropysics <http://packages.python.org/Astropysics/>`_ (Install with e.g. ``pip install astropysics --user``) - this is used for calculating co-ordinate distances, etc.

Usage
-----------------
The class ``ami.Reduce`` provides an easily scriptable interface to the ``reduce`` pipeline.
At this stage I haven't documented it, but in the meantime you can get started with the 
example scripts described below.

First try ``./list_ami_datasets.py --help`` to see your options. 
Unless you edit the defaults in the script, or happen to have an ami installation under */opt/ami*, then you will probably want to run::

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
---------
- Output detailed information for each file processed: rain, flagging, estimated noise, etc.
- Output full listings along with dataset groupings.
