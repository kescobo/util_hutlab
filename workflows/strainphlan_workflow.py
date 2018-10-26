#!/usr/bin/env python

"""
bioBakery Workflows: strainphlan

Copyright (c) 2018 Harvard School of Public Health

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import sys
import os, fnmatch

# import the workflow class from anadama2
from anadama2 import Workflow

# import the library of biobakery_workflow tasks for shotgun sequences
from biobakery_workflows.tasks import shotgun, general

# import the utilities functions and config settings from biobakery_workflows
from biobakery_workflows import utilities, config

# create a workflow instance, providing the version number and description
# the version number will appear when running this script with the "--version" option
# the description will appear when running this script with the "--help" option
workflow = Workflow(version="0.1", description="A workflow to run strainphlan")

# add the custom arguments to the workflow
workflow_config = config.ShotGun()
workflow.add_argument("input-extension", desc="the input file extension", default="fastq.gz", choices=["fastq.gz","fastq","fq.gz","fq","fasta","fasta.gz"])
workflow.add_argument("threads", desc="number of threads/cores for each task to use", default=1)
workflow.add_argument("bypass-taxonomic-profiling", desc="do not run the taxonomic profiling tasks (a tsv profile for each sequence file must be included in the input folder using the same sample name)", action="store_true")
workflow.add_argument("strain-profiling-options", desc="additional options when running the strain profiling step", default="")
workflow.add_argument("max-strains", desc="the max number of strains to profile", default=20, type=int)

# get the arguments from the command line
args = workflow.parse_args()

# get all input files with the input extension provided on the command line
# return an error if no files are found
input_files = utilities.find_files(args.input, extension=args.input_extension, exit_if_not_found=True)

### STEP #1: Run taxonomic profiling on all of the filtered files ###
if not args.bypass_taxonomic_profiling:
    merged_taxonomic_profile, taxonomy_tsv_files, taxonomy_sam_files = shotgun.taxonomic_profile(workflow,
        input_files,args.output,args.threads,args.input_extension)
elif:
    sample_names = utilities.sample_names(input_files,args.input_extension)
    tsv_profiles = utilities.name_files(sample_names, demultiplex_output_folder, tag="taxonomic_profile", extension="tsv")
    # check all of the expected profiles are found
    if len(tsv_profiles) != len(list(filter(os.path.isfile,tsv_profiles))):
        sys.exit("ERROR: Bypassing taxonomic profiling but all of the tsv taxonomy profile files are not found in the input folder. Expecting the following input files:\n"+"\n".join(tsv_profiles))
    # run taxonomic profile steps bypassing metaphlan2
    merged_taxonomic_profile, taxonomy_tsv_files, taxonomy_sam_files = shotgun.taxonomic_profile(workflow,
        tsv_profiles,args.output,args.threads,"tsv",already_profiled=True)
    # look for the sam profiles
    taxonomy_sam_files = utilities.name_files(sample_names, demultiplex_output_folder, tag="bowtie2", extension="sam")
    # if they do not all exist, then bypass strain profiling if not already set
    if len(taxonomy_sam_files) != len(list(filter(os.path.isfile,taxonomy_sam_files))):
        print("Warning: Bypassing taxonomic profiling but not all taxonomy sam files are present in the input folder. Strain profiling will be bypassed. Expecting the following input files:\n"+"\n".join(taxonomy_sam_files))
        args.bypass_strain_profiling = True

### STEP #2: Run strain profiling
# Provide taxonomic profiling output so top strains by abundance will be selected
if not args.bypass_strain_profiling:
    shotgun.strain_profile(workflow,taxonomy_sam_files,args.output,args.threads,
        workflow_config.strainphlan_db_reference,workflow_config.strainphlan_db_markers,merged_taxonomic_profile,
        args.strain_profiling_options,args.max_strains)

# start the workflow
workflow.go()
