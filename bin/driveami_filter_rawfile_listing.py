#!/usr/bin/env python
"""
Groups AMI datasets by pointing direction,
then dumps them in JSON format.
"""
from __future__ import print_function
import json
import argparse
import sys
import driveami

import logging
logging.basicConfig(level=logging.DEBUG)


def handle_args():
    """Outputs a file in JSON format listing AMI files, grouped by pointing."""

    parser = argparse.ArgumentParser(description="Filter listings for raw AMI data")

    parser.add_argument('listings',
                       help="Path to full-list (all datasets) input file")

    parser.add_argument('match',
                        help="String to match in observation groups.")

    parser.add_argument('-o', '--outfile', default=None,
                       help="Specify path to matching-datasets-list output file.")

    args = parser.parse_args()
    return args

def main():
    options = handle_args()
    with open(options.listings) as f:
        all_datasets, _ = driveami.load_listing(f,
                                 expected_datatype=driveami.Datatype.ami_la_raw)

    matching_datasets={}
    for grp_name, grp_info in all_datasets.iteritems():
        for fname in grp_info['files']:
            if str.upper(options.match) in str.upper(str(fname)):
                matching_datasets[grp_name]=grp_info
                break

    if len(matching_datasets)==0:
        print("No matches found")
        return 1

    if options.outfile is None:
        options.outfile = options.match+"_rawfiles.json"
    print('Datasets matching "{}" written to'.format(options.match),
          options.outfile)
    with open(options.outfile, 'w') as f:
        driveami.save_rawfile_listing(matching_datasets, f)


    return 0

if __name__ == "__main__":
    sys.exit(main())
