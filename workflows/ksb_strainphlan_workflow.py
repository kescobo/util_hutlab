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
    print(clade)

    cmd = "strainphlan.py --ifn_samples [markers] --output_dir [folder] --clades [clade]"

    genomes=set()
    reference_folder = os.environ['STRAINPHLAN_DB_REFERENCE']
    with open("/n/huttenhower_lab/tools/biobakery_workflows/biobakery_workflows/data/strainphlan_species_gcf.tsv") as file_handle:
        for line in file_handle:
            if line.startswith(clade):
                genomes.add(os.path.join(reference_folder,line.rstrip().split("\t")[-1]+".fna.bz2"))

    genomes = list(filter(os.path.isfile,genomes))

    if len(genomes):
        cmd += " --ifn_ref_genomes " + " --ifn_ref_genomes ".join(genomes)

    workflow.add_task_gridable(
        cmd,
        target=(),
        markers=os.path.join(markers, "*.markers"),
        folder=args.output,
        clade=clade,
        threads=args.threads,
        cores=args.threads,
        time=4*60, mem=8*1000)

workflow.go()
