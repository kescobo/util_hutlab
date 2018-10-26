from anadama2 import Workflow
import os

workflow = Workflow(version="0.1", description="A workflow to run strainphlan")

workflow.add_argument("clades", desc="output from --print_clades_only", default="clades.txt")
workflow.add_argument("markers", desc="folder containing markers", default="markers")
workflow.add_argument("threads", desc="nuber of threads", default=8)
args = workflow.parse_args()

clades = os.path.abspath(args.clades)
markers = os.path.abspath(args.markers)

clade_list = []

with open(clades) as handle:
    for l in handle:
        clade_list.append(l.split()[0])

print(clade_list)

for clade in clade_list:

    cmd = "strainphlan.py --ifn_samples {markers}*.markers --output_dir {folder} --clades {clade}"

    workflow.add_task_gridable(
        cmd,
        target=(),
        folder=args.output,
        clade=clade,
        threads=args.threads,
        cores=args.threads,
        time=4*60, mem=8*1000)

workflow.go()
