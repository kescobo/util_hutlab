#!/usr/bin/env python

from anadama2 import Workflow
import os

workflow = Workflow(version="0.0.2",
    description="A workflow to run PanPhlAn")

workflow.add_argument("threads", default=1,
    desc="number of threads for panphlan to use")
workflow.add_argument("dbfolder", default=None,
    desc="folder containing database")
workflow.add_argument("filesfile", default=None,
    desc="file with filepaths to run on (relative to input)")
workflow.add_argument("ref", default=None,
    desc="name of reference db")
workflow.add_argument("refs", default=None,
    desc="file with list of references (relative to dbfolder)")


args = workflow.parse_args()

in_files = workflow.get_input_files(".fastq.gz")
out_files = workflow.name_output_files(name=in_files, tag="panphlan_map", extension="csv.bz2")

if args.filesfile:
    with open(args.filesfile) as f:
        in_files = [l.strip() for l in f]

if args.dbfolder:
    cmd = "panphlan_map.py -c [reference] -i [depend] -o [target] -p [threads] --i_bowtie2_indexes [db]"
else:
    cmd = "panphlan_map.py -c [reference] -i [depend] -o [target] -p [threads]"


if args.ref:
    refs = [args.ref]
elif args.refs:
    r = open(args.refs, "r")
    refs = r.readlines()
    r.close()

for f in in_files:

    for ref in refs:
        if not os.path.isdir("{}/{}".format(args.output, ref)):
            os.makedirs("{}/{}".format(args.output, ref))
        fq_path = os.path.join(args.input, f)

        if args.filesfile:
            if not fq_path in files:
                skipped = open("{}/{}/skippedfiles.txt".format(args.output, ref), "a")
                skipped.write("{}\n".format(f))
                skipped.close()
        elif not os.path.isfile(fq_path):
            continue

        workflow.add_task_gridable(
            cmd, reference=ref,
            depend=fq_path,
            target="{}{}_panphlan_map.csv.bz2".format(args.output, f.strip(".fastq.gz")),
            folder=args.output,
            threads=args.threads,
            cores=args.threads,
            db=args.dbfolder,
            time=4*60, mem=8*1000)

workflow.go()
