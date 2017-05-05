#!/usr/bin/env python

"""
Groups AMI datasets by pointing direction,
then dumps them in JSON format.
"""
import argparse
import logging
import sys

import driveami
from driveami.environments import (default_ami_dir, default_ami_version)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(driveami.get_color_stdout_loghandler(logging.DEBUG))

_DESCRIPTION = """
Generate listings for raw AMI data.

Loads information about AMI raw-data files, using the AMI-REDUCE environment.

This information is then written to file in JSON format. Three JSON files 
are produced:

    <outfilename>_metadata.json - a full listing of all file data
    <outfilename>_by_id.json - a listing of filenames grouped by ID
    <outfilename>_by_pointing.json - a listing of filenames grouped by pointing.
"""

def handle_args():
    default_array = 'LA'
    default_full_listings_filename = 'all_ami_rawfiles'

    parser = argparse.ArgumentParser(
        description=_DESCRIPTION)

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
                        help="Output filename prefix (NB, will be suffixed "
                             "to create multiple output JSON files). "
                             "Default: '{}'".format(
                            default_full_listings_filename))

    parser.add_argument('--rawtext', action='store_true',
                        help="Save the file-listing rawtext when outputting"
                             "metadata file (useful for debugging crashes)."
                        )

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

    #Write file metadata
    with open(metadata_filename, 'w') as f:
        rawfile_dict = {fname: driveami.make_serializable(info) for fname, info
                        in r.files.iteritems()}
        if not options.rawtext:
            for _, fdict in rawfile_dict.iteritems():
                fdict.pop('raw_obs_listing_text')
        driveami.save_rawfile_listing(rawfile_dict, f)
    logger.info("Wrote file metadata listings to {}".format(metadata_filename))

    #Write listings grouped by ID
    logger.info("Grouping observations by target ID")
    id_groups = r.group_obs_by_target_id()
    with open(grouped_by_id_filename, 'w') as f:
        driveami.save_rawfile_listing(id_groups, f)
    logger.info("Wrote id-grouped file-listings to {}".format(grouped_by_id_filename))

    #Write listings grouped by pointing:
    logger.info("Grouping targets by pointing")
    pointing_groups = r.group_target_ids_by_pointing(id_groups,
                                                     pointing_tolerance_in_degrees=0.5)
    with open(grouped_by_pointing_filename, 'w') as f:
        driveami.save_rawfile_listing(pointing_groups, f)
    logger.info(
        "Wrote pointing-grouped file-listings to {}".format(
            grouped_by_pointing_filename))

    return 0


if __name__ == "__main__":
    sys.exit(main())
