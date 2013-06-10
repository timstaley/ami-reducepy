#!/usr/bin/env python

import argparse
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

    parser = argparse.ArgumentParser(prog='process_ami_data.py')
    parser.add_argument("-o", "--output-dir", default=default_output_dir,
                        help="Path to output directory (default is : " +
                            default_output_dir + ")")
    parser.add_argument("--ami", default=default_ami_dir,
                       help="Path to AMI directory, default: " + default_ami_dir)
    parser.add_argument('-s', '--script', help='Specify non-standard reduction script')

    parser.add_argument('groups_file', metavar='groups_to_process.json', nargs='?',
                        help='Specify JSON file listing groups for processing '
                             '(overrides all other file options)')

    parser.add_argument('-f', '--files', nargs='*',
                        help='Specify individual files for reduction')
    parser.add_argument('-g', '--group', dest='groupname', default='NOGROUP',
                        help='Specify group name for individually specified files')
    parser.add_argument('-r', '--array', default='LA',
                        help='Specify array (SA/LA) for individually specified files')

    values = parser.parse_args()
    values.ami_dir = os.path.expanduser(values.ami)
    values.output_dir = os.path.expanduser(values.output_dir)

    if values.script:
        with open(values.script) as f:
            values.script = f.read()

    if values.groups_file:
        print "Reducing files listed in:", values.groups_file
        values.array, data_groups = json.load(open(values.groups_file))
    elif values.files:
        data_groups = {values.groupname: {'files':values.files}}
    else:
        parser.print_help()
        sys.exit()

    print "SCRIPT:", values.script
    return values, data_groups

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
                    script=None):
    """Args:
    data_groups: Dictionary mapping groupname -> list of raw filenames
    output_dir: Folder where dataset group subfolders will be created.
    ami_dir: Top dir of the AMI ``reduce`` installation.
    array: 'LA' or 'SA' (Default: LA)
    """
    if not script:
        script = ami.scripts.standard_reduction
    r = ami.Reduce(ami_dir, array=array)
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
                                    reduce=r,
                                    script=script)
            except (ValueError, IOError) as e:
                logger.error("Hit exception reducing file: %s\n"
                             "Exception reads:\n%s\n",
                             rawfile, e)
                continue
            #Also save the group assignment in the listings: 
            file_info[ami.keys.group_name] = grp_name
            processed_files_info[rawfile] = ami.make_serializable(file_info)
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

    values, data_groups = handle_args()
    output_preamble_to_log(data_groups)
    processed_files_info = process_data_groups(data_groups,
                                values.output_dir,
                                values.ami_dir,
                                array=values.array,
                                script=values.script)
    with open('processed_files.json', 'w') as f:
        json.dump(processed_files_info, f, sort_keys=True, indent=4)
    sys.exit(0)
