#!/usr/bin/env python

import argparse
import os
from glob import glob
import re
import logging

parser = argparse.ArgumentParser(description="Get selected columns from table.")
parser.add_argument("table", help="tab-separated text file")
parser.add_argument("-c", "--columns", help="text file with one column name per line")
parser.add_argument("-o", "--output", help="name of output file", default=False)

parser.add_argument("-v", "--verbose", help="Display info status messages", action="store_true")
parser.add_argument("-q", "--quiet", help="Suppress most output", action="store_true")
parser.add_argument("-d", "--debug", help="Set logging to debug", action="store_true")

parser.add_argument("-l", "--log",
    help="File path for log file")

args = parser.parse_args()

logger = logging.getLogger("Column selector") # create logger
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
        logpath = os.path.join(logpath, "column_select.log")

    fh = logging.FileHandler(logpath)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

if args.output:
    out = open(args.out, "w+")
else:
    from sys import stdout
    out = stdout

columns = []
with open(args.columns, "r") as colfile:
    for line in colfile:
        columns.append(line.strip())

logger.info("Getting Columns: {}".format(columns))

with open(args.table, "r") as table:
    cols = table.readline().strip().split("\t")
    logger.debug(cols)
    colnos = [i for i, x in enumerate(cols) if x in columns]
    logger.debug(colnos)

    out.write("\t".join([cols[i] for i in colnos]))
    out.write("\n")

    for l in table.readlines():
        cols = l.split("\t")
        out.write("\t".join([cols[i] for i in colnos]))
        out.write("\n")

if args.output:
    out.close()
