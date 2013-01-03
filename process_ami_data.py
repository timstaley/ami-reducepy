#!/usr/bin/python

import optparse
import os
import sys
import logging
import json

import ami

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

def output_preamble_to_log(data_groups):
    logger.info("*************************************")
    logger.info("Processing with AMI reduce:\n"
                 "--------------------------------")
    for key in sorted(data_groups.keys()):
        logger.info("%s:", key)
        for f in data_groups[key][ami.keys.files]:
            logger.info("\t %s", f)
        logger.info("--------------------------------")
    logger.info("*************************************")

def process_data_groups(data_groups, output_dir, ami_dir,
                    array='LA',
                    script=ami.scripts.standard_reduction):
    """Args:
    data_groups: Dictionary mapping groupname -> list of raw filenames
    output_dir: Folder where dataset group subfolders will be created.
    ami_dir: Top dir of the AMI ``reduce`` installation.
    array: 'LA' or 'SA' (Default: LA)
    """
    r = ami.Reduce(ami_dir, array=array, logdir=output_dir)
    processed_files_info = {}
    for grp_name in sorted(data_groups.keys()):
        files = data_groups[grp_name][ami.keys.files]
        grp_dir = os.path.join(output_dir, grp_name, 'ami')
        ami.ensure_dir(grp_dir)
        for rawfile in files:
            try:
                logger.info("Reducing rawfile %s ...", rawfile)
                file_info = ami.process_rawfile(rawfile,
                                    output_dir=grp_dir,
                                    reduce=r)
            except (ValueError, IOError):
                logger.error("Hit exception reducing file: %s", rawfile)
                continue
            #Also save the group assignment in the listings: 
            file_info[rawfile][ami.keys.group_name] = grp_name
            processed_files_info.update(file_info)
    return processed_files_info

if __name__ == "__main__":
    logging.basicConfig(format='%(name)s:%(levelname)s:%(message)s',
                        filemode='w',
                        filename="ami-reduce.log",
                        level=logging.DEBUG)
    logger = logging.getLogger()
    log_stdout = logging.StreamHandler(sys.stdout)
    log_stdout.setLevel(logging.INFO)
    logger.addHandler(log_stdout)
#    logging.basicConfig(level=logging.WARN)

    options, groups_file = handle_args()
    if groups_file:
        array, data_groups = json.load(open(groups_file))

    output_preamble_to_log(data_groups)
    processed_files_info = process_data_groups(data_groups,
                                options.output_dir,
                                options.ami_dir,
                                array=array)
    with open('processed_files.json', 'w') as f:
        json.dump(processed_files_info, f, sort_keys=True, indent=4)
    sys.exit(0)
