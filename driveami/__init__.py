from __future__ import absolute_import
import logging
import os
import json
from colorlog import ColoredFormatter
import driveami.keys as keys
import driveami.scripts as scripts
from driveami.reduce import (Reduce, AmiVersion)

from driveami.serialization import (Datatype, make_serializable,
                                    save_calfile_listing, save_rawfile_listing,
                                    load_listing)


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


logger = logging.getLogger('ami')


def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)


def process_rawfile(rawfile, output_dir,
                    reduce,
                    script,
                    file_logging=True
                    ):
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
    write_command_overrides = {}
    if r.ami_version=='legacy':
        write_command_overrides['channels'] = '3-8'
    if r.files[rawfile]['raster']:
        write_command_overrides['fits_or_multi'] = 'multi'
        write_command_overrides['offsets'] = 'all'

    r.write_files(rawfile, output_dir,
                  write_command_overrides=write_command_overrides)

    r.files[rawfile][keys.obs_name] = os.path.splitext(rawfile)[0]
    info_filename = os.path.splitext(rawfile)[0] + '.json'
    with open(os.path.join(output_dir, info_filename), 'w') as f:
        json.dump(make_serializable(r.files[rawfile]), f,
                  sort_keys=True, indent=4)
    return r.files[rawfile]


def get_color_log_formatter():
    date_fmt = "%y-%m-%d (%a) %H:%M:%S"
    color_formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s:%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=date_fmt,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }
    )
    return color_formatter


def get_color_stdout_loghandler(level):
    stdout_loghandler = logging.StreamHandler()
    stdout_loghandler.setFormatter(get_color_log_formatter())
    stdout_loghandler.setLevel(level)
    return stdout_loghandler
