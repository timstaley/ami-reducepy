from __future__ import absolute_import
import logging
import os
import json
from ami.reduce import Reduce
from ami.keys import Keys
import ami.scripts as scripts

def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def output_preamble_to_log(data_groups):
    logging.info("*************************")
    logging.info("Processing data_groups:\n"
                 "--------------------------------")
    for key in sorted(data_groups.keys()):
        logging.info("%s:", key)
        for f in data_groups[key][Keys.files]:
            logging.info("\t %s", f)
        logging.info("--------------------------------")
    logging.info("*************************")

def process_data_groups(data_groups, output_dir, ami_dir,
                        array='LA',
                        script=scripts.standard_reduction):
    """Args:
    data_groups: Dictionary mapping groupname -> list of raw filenames
    output_dir: Folder where dataset group subfolders will be created.
    ami_dir: Top dir of the AMI ``reduce`` installation.
    array: 'LA' or 'SA' (Default: LA)
    """
    r = Reduce(ami_dir, array=array, logdir=output_dir)
    output_preamble_to_log(data_groups)
    processed_files_info = {}
    for grp_name in sorted(data_groups.keys()):
        files = data_groups[grp_name][Keys.files]
        grp_dir = os.path.join(output_dir, grp_name, 'ami')
        ensure_dir(grp_dir)
        for rawfile in files:
            try:
                logging.info("---------------------------------\n"
                             "Reducing rawfile %s ...", rawfile)
                r.set_active_file(rawfile, file_logdir=grp_dir)
                r.run_script(script)
                r.update_flagging_info()
                r.write_files(rawfile, output_dir=grp_dir)
                info_filename = os.path.splitext(rawfile)[0] + '_info.json'
                with open(os.path.join(grp_dir, info_filename), 'w') as f:
                    json.dump(r.files[rawfile], f, sort_keys=True, indent=4)
            except (ValueError, IOError):
                logging.error("Hit exception reducing file: %s", rawfile)
                continue
            r.files[rawfile][Keys.group_name] = grp_name
            r.files[rawfile][Keys.obs_name] = os.path.splitext(rawfile)[0]
            processed_files_info[rawfile] = r.files[rawfile]

    return processed_files_info
