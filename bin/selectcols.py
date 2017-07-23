#!/usr/bin/env python

import argparse
import os
from glob import glob
import re
import logging

""" Usage
Given a table file (eg .tsv or .csv), and a list of column names (one label per
line), this script will generate a new file with only the specified columns.

Using the -k flag will make the script keep the first column, even if it's not
in your list of labels (useful when the first column doesn't have a label).

```sh
$ $ python3 bin/selectcols.py tests/testfiles/table_with_columns.txt -c tests/testfiles/columns_to_select.txt -dk -s "\t" -o ~/Desktop/test.csv
2017-07-22,19:03:00 - INFO - Getting Columns: ['col1', 'col3']
2017-07-22,19:03:00 - DEBUG - ['', 'col1', 'col2', 'col3']
2017-07-22,19:03:00 - DEBUG - [0, 1, 3]
vpn6-252:util_hutlab kev$ cat ~/Desktop/test.csv
	col1	col3
row1	1	3
row2	4	6
row3	7	9
```

If no output is specified, it will go to STOUT, so you can redirect it. Example:

```sh
$ python3 bin/selectcols.py tests/testfiles/table_with_columns.txt -c tests/testfiles/columns_to_select.txt -dk -s "\t" >  ~/Desktop/test2.csv
2017-07-22,19:03:27 - INFO - Getting Columns: ['col1', 'col3']
2017-07-22,19:03:27 - DEBUG - ['', 'col1', 'col2', 'col3']
2017-07-22,19:03:27 - DEBUG - [0, 1, 3]
vpn6-252:util_hutlab kev$ cat ~/Desktop/test2.csv
	col1	col3
row1	1	3
row2	4	6
row3	7	9
```
"""

# Required arguments
parser = argparse.ArgumentParser(description="Get selected columns from table.", usage=__doc__)
parser.add_argument("table", help="table file")
parser.add_argument("-c", "--columns", help="text file with one column name per line", required=True)

# Optional arguments
parser.add_argument("-s", "--separator", help="separator for columns", default=",")
parser.add_argument("-o", "--output", help="name of output file", default=False)
parser.add_argument("-k", "--keep-first", help="Keep first column", action="store_true")

# Logging options
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
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)

if args.output:
    out = open(args.output, "w+")
else:
    from sys import stdout
    out = stdout

# Begin script
sep = args.separator
if sep == "\\t" or sep == "t" or sep == "tab":
    sep = "\t"
elif sep == "s" or sep == "space" or sep == " ":
    sep = " "
elif sep == "c" or sep == "comma" or sep == ",":
    sep = ","
else:
    raise ValueError("Invalid separator")

columns = []
with open(args.columns, "r") as colfile:
    for line in colfile:
        columns.append(line.strip())

logger.info("Getting Columns:")
logger.info(columns)

with open(args.table, "r") as table:
    cols = table.readline().rstrip("\n").split(sep)
    colnos = [i for i, x in enumerate(cols) if x in columns]

    columns = None
    if args.keep_first and not colnos[0] == 0:
        colnos.insert(0, 0)

    logger.debug(colnos)

    for i in colnos:
        out.write(cols[i])
        if not i == colnos[-1]:
            out.write(sep)
    out.write("\n")

    for l in table:
        cols = l.rstrip("\n").split(sep)
        for i in colnos:
            out.write(cols[i])
            if not i == colnos[-1]:
                out.write(sep)
        out.write("\n")

if args.output:
    out.close()
