import optparse
import os
import sys
import logging
import json

import ami
from ami.keys import ImageKeys as IKeys


def main():
    options, groups_file = handle_args(sys.argv[1:])
    if groups_file:
        array, groups = json.load(open(groups_file))
    print "Array:", array

    return 0


def handle_args(argv):
    """
    Default values for the script are defined here.
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

    parser.add_option("--amidir", default=default_ami_dir,
                       help="Path to AMI directory, default: " + default_ami_dir)

    options, args = parser.parse_args(argv)
    if len(args) != 1:
        parser.print_help()
        sys.exit(1)
    print "Reducing files listed in:", args[0]
    return options, args[0]

def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def output_preamble_to_log(groups):
    logging.info("*************************")
    logging.info("Processing:")
    for key in sorted(groups.keys()):
        logging.info("%s:", key)
        for f in groups[key][GroupKeys.files]:
            logging.info("\t %s", f)
        logging.info("--------------------------------")
    logging.info("*************************")



if __name__ == "__main__":
    logging.basicConfig(format='%(name)s:%(message)s',
                        filemode='w',
                        filename="ami-reduce.log",
                        level=logging.DEBUG)
    logger = logging.getLogger()
    log_stdout = logging.StreamHandler(sys.stdout)
    log_stdout.setLevel(logging.INFO)
    logger.addHandler(log_stdout)
    logging.debug('test')
    sys.exit(main())
