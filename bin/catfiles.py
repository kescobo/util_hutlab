#!/usr/bin/env python3

"""
Given a folder containing many fastq files, concatenate files following
user-defined regex pattern. Can also handle read-pairs.

For example, say I have the following folders containing fastq files:

```
seqencing/
    lane1/
        patient1_L1_r1.fastq
        patient1_L1_r2.fastq
        patient2_L1_r1.fastq
        patient2_L1_r2.fastq
        patient3_L1_r1.fastq
        patient3_L1_r2.fastq
    lane2/
        patient1_L2_r1.fastq
        patient1_L2_r2.fastq
        patient2_L2_r1.fastq
        patient2_L2_r2.fastq
        patient3_L2_r1.fastq
        patient3_L2_r2.fastq
```

I would use the regular expression `sequencing\/lane\d\/(patient\d)_L\d_r(1|2)\.fastq`

The first regex group (in this case, `patient\d`) defines which files will be
concatenated. For paired-end sequencing, the second regex group (which should
match `1|2`) defines mate pairs indicators.

If for some reason, your regex needs to define additional groups, you can use
the `--idgroup` and `--pairgroup` flags to specify which regex groups should be
matched.

The following command, used in the `sequencing/` directory above:

```sh
python catfiles.py -pr "sequencing\/lane\d\/(patient\d)_L\d_r(1|2)\.fastq" \
-o ./concatenated --verbose
```

...will create 6 files:

```
concatenated/
    patient1.R1.fastq
    patient1.R2.fastq
    patient2.R1.fastq
    patient2.R2.fastq
    patient3.R1.fastq
    patient3.R2.fastq
"""

import argparse
import os
from glob import glob
import re
import logging


parser = argparse.ArgumentParser(description="Concatenate fastq files from same subject.", usage=__doc__)
# Required Args
parser.add_argument("directory", help="folder containing fastq files")
parser.add_argument("-r", "--regex", help="pattern to find identifier and paired end id", required=True)

# Optional Args
parser.add_argument("-p", "--paired-end", help="look for paired-end reads", action="store_true")
parser.add_argument("-o", "--output", help="directory for concatenated files")
parser.add_argument("--idgroup", help="regex group containing sampleID", default=0, type=int)
parser.add_argument("--pairgroup", help="regex group paired-end ID", default=1, type=int)

parser.add_argument("--dryrun", help="output logs but do not write files", action="store_true")

# Logging options
parser.add_argument("-v", "--verbose", help="Display info status messages", action="store_true")
parser.add_argument("-q", "--quiet", help="Suppress most output", action="store_true")
parser.add_argument("--debug", help="Set logging to debug", action="store_true")

parser.add_argument("-l", "--log",
    help="File path for log file")

args = parser.parse_args()

logger = logging.getLogger("Concatenate") # create logger
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

if args.log and not args.dryrun:
    logpath = os.path.abspath(args.log)

    if os.path.isdir(logpath):
        logpath = os.path.join(logpath, "concatenate.log")

    fh = logging.FileHandler(logpath)
    if args.debug:
        fh.setLevel(logging.DEBUG)
    else:
        fh.setLevel(logging.INFO)
    logger.addHandler(fh)


output = args.output
directory = args.directory

files = glob(directory+"/**/*.fastq*", recursive=True)

paired_end = args.paired_end
regex = args.regex

idgroup = args.idgroup
pairgroup = args.pairgroup

logger.info("Looking for matching files")

files = [f for f in files if re.search(regex, f)]
if not files:
    logger.warning("no matching files found")

matches = [re.search(regex, x) for x in files]
ids = sorted(set([x.groups()[idgroup] for x in matches]))
logger.info("List of sample IDs:\n{}".format(ids))

if not os.path.isdir(output) and not args.dryrun:
    os.mkdir(output)

for i in ids:
    logger.info("Combining files for {}".format(i))
    if paired_end:
        f1 = [files[j] for j in range(len(files)) if matches[j].groups()[idgroup] == i and matches[j].groups()[pairgroup] == "1"]
        f2 = [files[j] for j in range(len(files)) if matches[j].groups()[idgroup] == i and matches[j].groups()[pairgroup] == "2"]
    else:
        f1 = [files[j] for j in range(len(files)) if matches[j].groups()[idgroup] == i]
        f2 = []

    if not f1:
        if paired_end:
            logger.warning("no matches found for first read pair")
        else:
            logger.warning("no matches found")
    else:
        f1.sort()

    if paired_end and not f2:
        logger.warning("no matches found for second read pair")
    elif paired_end:
        f2.sort()

    for f in f1:
        if paired_end:
            logger.info("1st pair - using file {}".format(os.path.basename(f)))
        else:
            logger.info("Using file {}".format(os.path.basename(f)))

    for f in f2:
        logger.info("2nd pair - using file {}".format(os.path.basename(f)))

    logger.info("Writing to {}".format(os.path.basename("{}.R1.fastq".format(i))))
    if not args.dryrun:
        with open(os.path.join(output, "{}.R1.fastq".format(i)), "w+b") as out1:
            for f in f1:
                with open(f, "rb") as infile:
                    out1.write(infile.read())
    if paired_end:
        logger.info("Writing to {}".format(os.path.basename("{}.R2.fastq".format(i))))
        if not args.dryrun:
            with open(os.path.join(output, "{}.R2.fastq".format(i)), "w+b") as out2:
                for f in f2:
                    with open(f, "rb") as infile:
                        out2.write(infile.read())
