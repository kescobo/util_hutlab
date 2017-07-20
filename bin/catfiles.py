#!/usr/bin/env python

import argparse
import os
from glob import glob
import re
import logging

parser = argparse.ArgumentParser(description="Concatenate fastq files from same subject.")
parser.add_argument("directory", help="folder containing fastq files")
parser.add_argument("-r", "--regex", help="pattern to find identifier and paired end id")
parser.add_argument("-p", "--paired-end", help="pattern to find identifier and paired end id", action="store_true")
parser.add_argument("-o", "--output", help="directory for concatenated files")
parser.add_argument("--dryrun", help="output logs but do not write files", action="store_true")

parser.add_argument("-v", "--verbose", help="Display info status messages", action="store_true")
parser.add_argument("-q", "--quiet", help="Suppress most output", action="store_true")
parser.add_argument("--debug", help="Set logging to debug", action="store_true")

parser.add_argument("-l", "--log",
    help="File path for log file")

args = parser.parse_args()

logpath = None
if args.log:
    logpath = os.path.abspath(args.log)
    if os.path.isdir(logpath):
        logpath = os.path.join(logpath, "kvasir.log")
else:
    logpath = ("kvasir.log")

logger = logging.getLogger("Concatenate") # create logger
sh = logging.StreamHandler()
fh = logging.FileHandler(logpath)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')
sh.setFormatter(formatter)
fh.setFormatter(formatter)

# set level based on args
if args.debug:
    sh.setLevel(logging.DEBUG)
    fh.setLevel(logging.DEBUG)
elif args.verbose:
    sh.setLevel(logging.INFO)
    fh.setLevel(logging.INFO)
elif args.quiet:
    sh.setLevel(logging.ERROR)
    fh.setLevel(logging.ERROR)
else:
    sh.setLevel(logging.WARNING)
    fh.setLevel(logging.WARNING)

logger.addHandler(sh) # add handler to logger
logger.addHandler(fh)

output = args.output
directory = args.directory

files = glob(directory+"/**/*.fastq")

paired_end = args.paired_end
regex = args.regex

matches = [re.search(regex, x) for x in files]
ids = sorted(set([x.groups()[0] for x in matches]))
logging.info("List of sample IDs:\n{}".format(ids))

if not os.path.isdir(output):
    os.mkdir(output)

for i in ids:
    logging.info("Combining files for {}".format(i))
    if paired_end:
        f1 = [files[j] for j in range(len(files)) if matches[j].groups()[0] == i and matches[j].groups()[1] == "1"]
        f2 = [files[j] for j in range(len(files)) if matches[j].groups()[0] == i and matches[j].groups()[1] == "2"]

        if not f1:
            logging.warning("no matches found for first read pair")
        if not f2:
            logging.warning("no matches found for second read pair")

        for f in f1:
            logging.info("1st pair - using file {}".format(os.path.basename(f)))
        for f in f2:
            logging.info("2st pair - using file {}".format(os.path.basename(f)))


        with open(os.path.join(output, "{}.R2.fastq".format(i)), "w+") as out2:
            logging.info("Writing to {}".format(out2.name))
            for f in f2:
                with open(f, "r") as infile:
                    if not args.dryrun:
                        out2.write(infile.read())
    else:
        f1 = [files[j] for j in range(len(files)) if matches[j].groups()[0] == i]
        if not f1:
            logging.warning("no matches found")
        for f in f1:
            logging.info("Using file {}".format(os.path.basename(f)))

    with open(os.path.join(output, "{}.R1.fastq".format(i)), "w+") as out1:
        logging.info("Writing to {}".format(out1.name))
        for f in f1:
            with open(f, "r") as infile:
                if not args.dryrun:
                    out1.write(infile.read())
