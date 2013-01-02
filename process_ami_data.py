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
    processed_files_info = ami.process_data_groups(data_groups,
                                options.output_dir,
                                options.ami_dir,
                                array=array)
    with open('processed_files.json', 'w') as f:
        json.dump(processed_files_info, f, sort_keys=True, indent=4)
    sys.exit(0)
