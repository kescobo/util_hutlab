import os

#!/usr/bin/env python

import argparse
import os
import re
import logging

parser = argparse.ArgumentParser(description="Deconvolute fastq file based on read counts.")


# Required arguments
parser.add_argument("input-folder", help="folder containing fastq files to separate")
parser.add_argument("readcounts", help="file with read_counts for each file")

# Optional arguments
parser.add_argument("-o", "--out", help="folder for output")
parser.add_argument("--dryrun", help="output logs but do not write files", action="store_true")


# Logging options
parser.add_argument("-v", "--verbose", help="Display info status messages", action="store_true")
parser.add_argument("-q", "--quiet", help="Suppress most output", action="store_true")
parser.add_argument("-d", "--debug", help="Set logging to debug", action="store_true")
parser.add_argument("-l", "--log", help="File path for log file")


args = parser.parse_args()

logger = logging.getLogger("Deconvolute") # create logger
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')

sh = logging.StreamHandler()
sh.setFormatter(formatter)

# set level based on args
if args.debug:
    sh.setLevel(logging.DEBUG)
elif args.verbose:
    sh.setLevel(logging.INFO)
elif args.quiet:
    sh.setLevel(logging.ERROR)
else:
    sh.setLevel(logging.WARNING)

logger.addHandler(sh) # add handler to logger

if args.log:
    logpath = os.path.abspath(args.log)

    if os.path.isdir(logpath):
        logpath = os.path.join(logpath, "crap.log")

    fh = logging.FileHandler(logpath)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

if args.out:
    out = open(args.out, "w+")
else:
    from sys import stdout
    out = stdout


# Functions

def readwrite(count_dict, pair, key):
    logger.debug("reading from {}.R{}.fastq".format(key, pair))
    with open("{}.R{}.fastq".format(key, pair)) as r1:
        current = 1
        stop = 0
        for i in sorted(count_dict[key]):
            stop += count_dict[key][i] * 4
            logger.info("reading lines {}:{}".format(current, stop))
            logger.info("writing to {}_{}_{}.fastq".format(i, key, pair))
            with open("{}_{}_{}.fastq".format(i, key, pair), "w+") as outfile:
                while current <= stop:
                    l = r1.readline()
                    current += 1
                    if not args.dryrun:
                        outfile.write(l)

# Begin script
counts = {}
with open(args.readcounts, "r") as rcounts:
    for c in rcounts:
        i, f, c = c.split("\t")
        c = int(c)
        if i in counts:
            counts[i][f] = c
        else:
            counts[i] = {f:c}

for k in sorted(counts):
    readwrite(counts, 1, k)
    readwrite(counts, 2, k)
