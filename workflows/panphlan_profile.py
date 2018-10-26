#!/usr/bin/env python

from anadama2 import Workflow
import os

workflow = Workflow(version="0.0.1",
    description="A workflow to run PanPhlAn")

workflow.add_argument("dbfolder", default=None,
    desc="folder containing database")
workflow.add_argument("ref", default=None,
    desc="name of reference db")
workflow.add_argument("refs", default=None,
    desc="file with list of references (relative to dbfolder)")

args = workflow.parse_args()

cmd = "panphlan_profile.py -c {0} -i {0}/ --o_dna [target] --add_strains"

if args.dbfolder:
    cmd += " --i_bowtie2_indexes {}".format(args.dbfolder)

if args.ref:
    refs = [args.ref]
elif args.refs:
    r = open(args.refs, "r")
    refs = [l.strip() for l in r]
    r.close()

for ref in refs:
    if os.path.isdir(ref):
        workflow.add_task_gridable(
            cmd.format(ref, ref),
            target="{}profiles/{}_pa.tsv".format(output,ref),
            cores=1,
            time=30, mem=1000)

workflow.go()
