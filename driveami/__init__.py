from __future__ import absolute_import
import logging
import os
import json
import driveami.keys as keys
import driveami.scripts as scripts
from driveami.reduce import Reduce

logger = logging.getLogger('ami')

datetime_format = '%Y-%m-%d %H:%M:%S'

def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def make_serializable(file_info_dict):
    """Returns a JSON serializable version of a file info dictionary.

    E.g. the dict returned by the `process_rawfile` routine.
    """
    d = file_info_dict.copy()
    # UTC datetime
    d[keys.time_ut] = [t.strftime(datetime_format) for t in d[keys.time_ut]]
    return d

def process_rawfile(rawfile, output_dir,
                    reduce,
                    file_logging=True,
                    script=scripts.standard_reduction):
    """
    A convenience function applying sensible defaults to reduce a rawfile.

    Args:
    rawfile: Name of a file in the ami data dir, e.g. "SWIFT121101-121101.raw"
    output_dir: Folder where UVFITS for the target and calibrator will be output.
    reduce: instance of ami.Reduce
    array: 'LA' or 'SA' (Default: LA)
    script: Reduction commands.

    Returns:
        - A dictionary containing information about the rawfile,
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
    r.write_files(rawfile, output_dir,
                  write_command_overrides={'channels':'3-8'})
    r.files[rawfile][keys.obs_name] = os.path.splitext(rawfile)[0]
    info_filename = os.path.splitext(rawfile)[0] + '.json'
    with open(os.path.join(output_dir, info_filename), 'w') as f:
        json.dump(make_serializable(r.files[rawfile]), f,
                  sort_keys=True, indent=4)
    return r.files[rawfile]
