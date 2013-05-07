#!/usr/bin/env python

"""
Groups AMI datasets by pointing direction,
then dumps them in JSON format.
"""
import json
import optparse
import sys

import ami


def main():
    options = handle_args(sys.argv[1:])
    r = ami.Reduce(options.ami_dir, options.array)
    named_groups = r.group_pointings()
    with open(options.datasets, 'w') as f:
        json.dump([r.array , named_groups], f,
                  sort_keys=True, indent=4)
    return 0
    
def handle_args(argv):
    """
    Returns tuple (options_object, outputfilename)
    """
    default_ami_dir = "/opt/ami" 
    default_array = 'LA'
    default_short_listings_filename = 'datasets.json'
    default_full_listings_filename = 'full_listings.json'
    
    usage = """usage: %prog [options] outputfile\n"""\
    """Outputs a file in JSON format listing AMI files, grouped by pointing."""
    
    parser = optparse.OptionParser(usage)
                
    parser.add_option("--ami-dir", default=default_ami_dir, 
                       help="Path to AMI directory, default: " + default_ami_dir)
    parser.add_option("--array", default=default_array,
                       help="Array data to work with (SA/LA), defaults to: " 
                       + default_array)
    
    parser.add_option('-d', '--datasets', default=default_short_listings_filename, 
                       help="Path to dataset groupings output file, default: " 
                                + default_short_listings_filename)
    
    parser.add_option('-l', '--listings', default=default_full_listings_filename, 
                       help="Path to obs listings output file, default: " 
                                + default_full_listings_filename)

    options, args =  parser.parse_args(argv)
    print "Writing data details to files:", options.datasets, ",",options.listings
    return options

if __name__ == "__main__":
    sys.exit(main())
