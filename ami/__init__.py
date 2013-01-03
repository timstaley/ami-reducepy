from __future__ import absolute_import
import logging
import os
import json
from ami.reduce import Reduce
import ami.keys as keys
import ami.scripts as scripts

logger = logging.getLogger('ami')

def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)



def process_rawfile(rawfile, output_dir,
                    reduce,
                    file_logging=True,
                    script=scripts.standard_reduction):
    """Args:
    rawfile: Name of a file in the ami data dir, e.g. "SWIFT121101-121101.raw"
    output_dir: Folder where UVFITS for the target and calibrator will be output.
    reduce: instance of ami.Reduce
    array: 'LA' or 'SA' (Default: LA)
    script: Reduction commands.

    Returns:
        - A nested dictionary containing information about the rawfile,
          e.g. pointing, calibrator name, rain modulation.
          See also: ``ami.keys``
    """
    r = reduce
    if file_logging:
        file_logdir = output_dir
    else:
        file_logdir = None
    r.set_active_file(rawfile, file_logdir)
    r.run_script(script)
    r.update_flagging_info()
    r.write_files(rawfile, output_dir)
    info_filename = os.path.splitext(rawfile)[0] + '_info.json'
    with open(os.path.join(output_dir, info_filename), 'w') as f:
        json.dump(r.files[rawfile], f, sort_keys=True, indent=4)
    r.files[rawfile][keys.obs_name] = os.path.splitext(rawfile)[0]
    return {rawfile: r.files[rawfile]}
