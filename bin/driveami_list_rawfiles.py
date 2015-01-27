#!/usr/bin/env python

"""
Groups AMI datasets by pointing direction,
then dumps them in JSON format.
"""
import json
import argparse
import sys
import os

import logging

logging.basicConfig(level=logging.DEBUG)
import driveami
from driveami.environments import default_ami_dir

logger = logging.getLogger("list_ami_datasets")


def handle_args():
    default_array = 'LA'
    default_full_listings_filename = 'all_ami_rawfiles'

    parser = argparse.ArgumentParser(
        description="Generate listings for raw AMI data")

    parser.add_argument("--ami", default=default_ami_dir,
                        help="Path to AMI directory, default: " + default_ami_dir)

    parser.add_argument("--array", default=default_array,
                        help="Array data to work with (SA/LA), defaults to: "
                             + default_array)

    parser.add_argument('-o', '--outfile',
                        default=default_full_listings_filename,
                        help="Path to output file (NB, will be suffixed "
                             "to create two versions) "
                             "default: "
                             + default_full_listings_filename)

    args = parser.parse_args()
    print "Will output listings of all datasets to :", args.outfile
    return args


def main():
    options = handle_args()
    grouped_by_id_filename = options.outfile + '_by_id.json'
    grouped_by_pointing_filename = options.outfile + '_by_pointing.json'

    r = driveami.Reduce(options.ami, options.array)
    logger.info("Loading observation metadata.")
    r.load_obs_info()
    logger.info("Grouping observations by target ID")
    id_groups = r.group_obs_by_target_id()
    with open(grouped_by_id_filename, 'w') as f:
        driveami.save_rawfile_listing(id_groups, f)
    logger.info("Grouping targets by pointing")
    pointing_groups = r.group_target_ids_by_pointing(id_groups,
                                                     pointing_tolerance_in_degrees=0.5)
    with open(grouped_by_pointing_filename, 'w') as f:
        driveami.save_rawfile_listing(pointing_groups, f)

    return 0


if __name__ == "__main__":
    sys.exit(main())
