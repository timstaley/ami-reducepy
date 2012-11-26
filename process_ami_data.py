#!/usr/bin/python

import optparse
import os
import sys
import logging
import json

import ami
from ami.keys import (GroupKeys, RawKeys)

standard_reduction_script = \
r"""
flag all
flag int \
subtract modmeans \
subtract zeros \
subtract means \
update pcal \
fft \
frotate forward y n \
flag amp all all field yes 1 \
apply rain \
flag amp all all field no 0.432 1 \
flag amp all all field no 0.1 20 \
frotate forward n y \
cal inter \
reweight \
show flagging no yes \
smooth 50 \
show flagging no yes \
flag bad cal all all all \
scan dat cal yes \
scan dat field yes \
show flagging no yes \
"""

def main():
    options, groups_file = handle_args(sys.argv[1:])
    if groups_file:
        array, groups = json.load(open(groups_file))
    r = ami.Reduce(options.ami_dir, array=array, logdir=options.output_dir)
    output_preamble_to_log(groups)
    for grp_name in sorted(groups.keys()):
        files = groups[grp_name][GroupKeys.files]
        grp_dir = os.path.join(options.output_dir, grp_name, 'ami')
        ensure_dir(grp_dir)
        processed_files_info = {}
        for rawfile in files:
            try:
                logging.info("---------------------------------\n"
                             "Reducing rawfile %s ...", rawfile)
                r.set_active_file(rawfile, file_logdir=grp_dir)
                r.run_script(standard_reduction_script)
                r.update_flagging_info()
                r.write_files(rawfile, output_dir=grp_dir)
                info_filename = os.path.splitext(rawfile)[0]+'_info.json'
                with open(os.path.join(grp_dir, info_filename),'w') as f:
                    json.dump(r.files[rawfile], f)
            except (ValueError, IOError):
                logging.error("Hit exception reducing file: %s", rawfile)
                continue
            processed_files_info[rawfile] = r.files[rawfile]
    
    with open('processed_files.json', 'w') as f:
        json.dump(processed_files_info, f, sort_keys=True, indent=4)

    return 0


def handle_args(argv):
    """
    Default values are defined here.
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

    parser.add_option("--ami-dir", default=default_ami_dir,
                       help="Path to AMI directory, default: " + default_ami_dir)

    options, args = parser.parse_args(argv)
    options.ami_dir = os.path.expanduser(options.ami_dir)
    options.output_dir = os.path.expanduser(options.output_dir)
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
    logging.info("Processing groups:\n"
                 "--------------------------------")
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
    sys.exit(main())
