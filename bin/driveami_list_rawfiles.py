#!/usr/bin/env python

"""
Groups AMI datasets by pointing direction,
then dumps them in JSON format.
"""
import argparse
import sys
import logging

import driveami
from driveami.environments import (default_ami_dir, default_ami_version)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(driveami.get_color_stdout_loghandler(logging.DEBUG))


def handle_args():
    default_array = 'LA'
    default_full_listings_filename = 'all_ami_rawfiles'

    parser = argparse.ArgumentParser(
        description="Generate listings for raw AMI data")

    parser.add_argument("--amidir", default=default_ami_dir,
                        help="Path to AMI directory, default: " + default_ami_dir)

    parser.add_argument(
        "--amiversion", default=default_ami_version,
        help="AMI version (digital/legacy), default: " + default_ami_version,
        choices=['digital', 'legacy'])

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
    logger.info("Will output listings of all datasets to '{}'".format(
        args.outfile))
    return args


def main():
    options = handle_args()
    grouped_by_id_filename = options.outfile + '_by_id.json'
    grouped_by_pointing_filename = options.outfile + '_by_pointing.json'
    metadata_filename = options.outfile + '_metadata.json'

    r = driveami.Reduce(options.amidir, options.amiversion, options.array)
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

    with open(metadata_filename, 'w') as f:
        rawfile_dict = {fname: driveami.make_serializable(info) for fname, info
                        in r.files.iteritems()}
        driveami.save_rawfile_listing(rawfile_dict, f)

    return 0


if __name__ == "__main__":
    sys.exit(main())
