#!/usr/bin/python
"""
Groups AMI datasets by pointing direction,
then dumps them in JSON format.
"""
import json
import optparse
import sys

import ami


def main():
    options, outputfilename = handle_args(sys.argv[1:])
    r = ami.Reduce(options.amidir)
    named_groups = r.group_pointings()
    json.dump(named_groups, open(outputfilename, 'w'),
              sort_keys=True, indent=4)
    return 0
    
def handle_args(argv):
    """
    Returns tuple (options_object, outputfilename)
    """
    default_ami_dir = "/opt/ami" 
    default_array = 'LA'
    
    usage = """usage: %prog [options] outputfile\n"""\
    """Outputs a file in JSON format listing AMI files, grouped by pointing."""
    
    parser = optparse.OptionParser(usage)
        
        
    parser.add_option("--amidir", default=default_ami_dir, 
                       help="Path to AMI directory, default: " + default_ami_dir)
    parser.add_option("--array", default=default_array,
                       help="Array data to work with (SA/LA), defaults to: " 
                       + default_array)

    options, args =  parser.parse_args(argv)
    if len(args)!=1:
        parser.print_help()
        sys.exit(1)
    print "Will output listings to file:", args[0]
    return options, args[0]

if __name__ == "__main__":
    sys.exit(main())
