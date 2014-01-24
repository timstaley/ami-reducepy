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
    with open(options.infile) as f:
        array, all_datasets = json.load(f)


    matching_datasets={}
    for grp_name, grp_info in all_datasets.iteritems():
        for fname in grp_info['files']:
            if str.upper(options.matchstring) in str.upper(str(fname)):
                matching_datasets[grp_name]=grp_info
                break

    if len(matching_datasets)==0:
        print "No matches found"
        return 1

    if options.outfile is None:
        options.outfile = options.matchstring+"_datasets.json"
    print'Datasets matching "{}" written to'.format(options.matchstring),options.outfile
    with open(options.outfile, 'w') as f:
        json.dump([array , matching_datasets], f,
                  sort_keys=True, indent=4)


    return 0

def handle_args():
    default_full_listings_filename = 'all_datasets.json'

    usage = """usage: %prog [options] outputfile\n"""\
    """Outputs a file in JSON format listing AMI files, grouped by pointing."""

    parser = argparse.ArgumentParser(description="Filter listings for raw AMI data")

    parser.add_argument('-i','--infile', default=default_full_listings_filename,
                       help="Path to full-list (all datasets) input file, default: "
                                + default_full_listings_filename)

    parser.add_argument('-o', '--outfile', default=None,
                       help="Specify path to matching-datasets-list output file.")

    parser.add_argument('matchstring')
    # parser.add_argument('-l', '--listings', default=default_full_listings_filename,
    #                    help="Path to obs listings output file, default: "
    #                             + default_full_listings_filename)

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    sys.exit(main())
