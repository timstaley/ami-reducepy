#!/usr/bin/env python

"""
Groups AMI datasets by pointing direction,
then dumps them in JSON format.
"""
import json
import argparse
import sys

import logging
logging.basicConfig(level=logging.DEBUG)
import driveami as ami


def main():
    options = handle_args()
    r = ami.Reduce(options.ami, options.array)
    all_datasets = r.group_pointings()
    with open(options.outfile, 'w') as f:
        json.dump([r.array , all_datasets], f,
                  sort_keys=True, indent=4)

    return 0

def handle_args():
    default_ami_dir = "/data2/ami"
    default_array = 'LA'
    default_full_listings_filename = 'all_datasets.json'
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
