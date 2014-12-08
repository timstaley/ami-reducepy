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
import driveami as ami

logger = logging.getLogger("list_ami_datasets")

def main():
    options = handle_args()
    grouped_by_id_filename = options.outfile+'_by_id.json'
    grouped_by_pointing_filename = options.outfile+'_by_pointing.json'

    r = ami.Reduce(options.ami, options.array)
    logger.info("Loading observation metadata.")
    r.load_obs_info()
    logger.info("Grouping observations by target ID")
    id_groups = r.group_obs_by_target_id()
    with open(grouped_by_id_filename, 'w') as f:
        json.dump([r.array , id_groups], f,
                  sort_keys=True, indent=4)
    logger.info("Grouping targets by pointing")
    pointing_groups = r.group_target_ids_by_pointing(id_groups,
                                             pointing_tolerance_in_degrees=0.5)
    with open(grouped_by_pointing_filename, 'w') as f:
        json.dump([r.array , pointing_groups], f,
                  sort_keys=True, indent=4)

    return 0

def handle_args():
    default_ami_dir = os.path.expanduser("~/ami")
    default_array = 'LA'
    default_full_listings_filename = 'all_datasets'
    default_matching_listings_filename = 'matching_datasets.json'
    # default_full_listings_filename = 'full_listings.json'

    usage = """usage: %prog [options] outputfile\n"""\
    """Outputs a file in JSON format listing AMI files, grouped by pointing."""

    parser = argparse.ArgumentParser(description="Generate listings for raw AMI data")

    parser.add_argument("--ami", default=default_ami_dir,
                       help="Path to AMI directory, default: " + default_ami_dir)
    parser.add_argument("--array", default=default_array,
                       help="Array data to work with (SA/LA), defaults to: "
                       + default_array)

    parser.add_argument('-o', '--outfile', default=default_full_listings_filename,
                       help="Path to full-list (all datasets) output file, default: "
                                + default_full_listings_filename)



    args = parser.parse_args()
    print "Will output listings of all datasets to :", args.outfile
    return args

if __name__ == "__main__":
    sys.exit(main())
