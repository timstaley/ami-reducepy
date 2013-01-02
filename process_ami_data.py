#!/usr/bin/python

import optparse
import os
import sys
import logging
import json

import ami
from ami.keys import  Keys

standard_reduction_script = \
r"""
flag all
flag int \
subtract modmeans \
subtract zeros \
subtract means \
update pcal \
fft \
frotate forward y n \
flag amp all all field yes 1 \
apply rain \
flag amp all all field no 0.432 1 \
flag amp all all field no 0.1 20 \
frotate forward n y \
cal inter \
reweight \
show flagging no yes \
smooth 50 \
show flagging no yes \
flag bad cal all all all \
scan dat cal yes \
scan dat field yes \
show flagging no yes \
"""

def main(data_groups, output_dir, ami_dir, array='LA'):
    """Args:
    data_groups: Dictionary mapping groupname -> list of raw filenames
    output_dir: Folder where dataset group subfolders will be created.
    ami_dir: Top dir of the AMI ``reduce`` installation.
    array: 'LA' or 'SA' (Default: LA)
    """
    r = ami.Reduce(ami_dir, array=array, logdir=output_dir)
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
                r.run_script(standard_reduction_script)
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

def handle_args():
    """
    Default values are defined here.
    """
    default_output_dir = os.path.expanduser("~/ami_results")
    default_ami_dir = "/opt/ami"
    usage = """usage: %prog [options] datasets_to_process.json\n"""
    parser = optparse.OptionParser(usage)

    parser.add_option("-o", "--output-dir", default=default_output_dir,
                      help="Path to output directory (default is : " +
                            default_output_dir + ")")
#    parser.add_option("-r", "--reprocess", action="store_true",
#                      dest="reprocess", default=True,
#          help="Reprocess with the AMI pipeline even if the output exists "
#                "(default False)")

    parser.add_option("--ami-dir", default=default_ami_dir,
                       help="Path to AMI directory, default: " + default_ami_dir)

    options, args = parser.parse_args()
    options.ami_dir = os.path.expanduser(options.ami_dir)
    options.output_dir = os.path.expanduser(options.output_dir)
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    print "Reducing files listed in:", args[0]
    return options, args[0]


if __name__ == "__main__":
    logging.basicConfig(format='%(name)s:%(message)s',
                        filemode='w',
                        filename="ami-reduce.log",
                        level=logging.DEBUG)
    logger = logging.getLogger()
    log_stdout = logging.StreamHandler(sys.stdout)
    log_stdout.setLevel(logging.INFO)
    logger.addHandler(log_stdout)

    options, groups_file = handle_args()
    if groups_file:
        array, data_groups = json.load(open(groups_file))
    processed_files_info = main(data_groups,
                                options.output_dir,
                                options.ami_dir,
                                array=array)
    with open('processed_files.json', 'w') as f:
        json.dump(processed_files_info, f, sort_keys=True, indent=4)
    sys.exit(0)
