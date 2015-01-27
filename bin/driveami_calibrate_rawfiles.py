#!/usr/bin/env python

import argparse
import os
import sys
import logging
import json

import driveami
from driveami.environments import (default_ami_dir, default_output_dir)

def handle_args():
    """
    Default values are defined here.
    """
    parser = argparse.ArgumentParser(prog='process_ami_data.py')
    parser.add_argument("-w", "--working-dir", default=default_output_dir,
                        help="Top level data-output directory, default is : " +
                            default_output_dir)

    parser.add_argument('-o', '--outfile', nargs='?',
                        help='Specify filename for output listing of calibrated '
                             'data')

    parser.add_argument('groups_file', metavar='groups_to_process.json', nargs='?',
                        help='Specify file listing rawfiles for processing '
                             '(overrides all other file options)')

    parser.add_argument("--ami", default=default_ami_dir,
                       help="Path to AMI directory, default: " + default_ami_dir)

    parser.add_argument('-s', '--script', help='Specify non-standard reduction script')

    parser.add_argument('-f', '--files', nargs='*',
                        help='Specify individual files for reduction')

    parser.add_argument('-g', '--group', dest='groupname', default='NOGROUP',
                        help='Specify group name for individually specified files')

    # parser.add_argument('-r', '--array', default='LA',
    #                     help='Specify array (SA/LA) for individually specified files')

    options = parser.parse_args()
    options.ami_dir = os.path.expanduser(options.ami)
    options.working_dir = os.path.expanduser(options.working_dir)

    if options.script:
        with open(options.script) as f:
            options.script = f.read()

    if options.groups_file:
        print "Reducing files listed in:", options.groups_file
        with open(options.groups_file) as f:
            data_groups, _ = driveami.load_listing(f,
                               expected_datatype=driveami.Datatype.ami_la_raw)
    elif options.files:
        data_groups = {options.groupname: {'files':options.files}}
    else:
        parser.print_help()
        sys.exit()

    # print "SCRIPT:", options.script
    return options, data_groups

def output_preamble_to_log(data_groups):
    logger.info("*************************************")
    logger.info("Processing with AMI reduce:\n"
                 "--------------------------------")
    for key in sorted(data_groups.keys()):
        logger.info("%s:", key)
        for f in data_groups[key][driveami.keys.files]:
            logger.info("\t %s", f)
        logger.info("--------------------------------")
    logger.info("*************************************")

def process_data_groups(data_groups, output_dir, ami_dir,
                    array='LA',
                    script=None):
    """Args:
    data_groups: Dictionary mapping groupname -> list of raw filenames
    output_dir: Folder where dataset group subfolders will be created.
    ami_dir: Top dir of the AMI ``reduce`` installation.
    array: 'LA' or 'SA' (Default: LA)
    """
    if not script:
        script = driveami.scripts.standard_reduction
    r = driveami.Reduce(ami_dir, array=array)
    processed_files_info = {}
    for grp_name in sorted(data_groups.keys()):
        files = data_groups[grp_name][driveami.keys.files]
        grp_dir = os.path.join(output_dir, grp_name, 'ami')
        driveami.ensure_dir(grp_dir)
        logger.info('Calibrating rawfiles and writing to {}'.format(grp_dir))
        for rawfile in files:
            try:
                logger.info("Reducing rawfile %s ...", rawfile)
                file_info = driveami.process_rawfile(rawfile,
                                    output_dir=grp_dir,
                                    reduce=r,
                                    script=script)
            except (ValueError, IOError) as e:
                logger.exception("Hit exception reducing file: %s\n"
                             "Exception reads:\n%s\n",
                             rawfile, e)
                continue
            # Also save the group assignment in the listings:
            file_info[driveami.keys.group_name] = grp_name
            processed_files_info[rawfile] = driveami.make_serializable(file_info)
    return processed_files_info


def main():
    options, data_groups = handle_args()
    output_preamble_to_log(data_groups)
    processed_files_info = process_data_groups(data_groups,
                                options.working_dir,
                                options.ami_dir,
                                array='LA',
                                script=options.script)

    output_listings_filepath = options.outfile
    if output_listings_filepath is None:
        output_listings_filepath = "calibrated_files.json"
    with open(output_listings_filepath, 'w') as f:
        driveami.save_calfile_listing(processed_files_info, f)
    sys.exit(0)


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
    main()