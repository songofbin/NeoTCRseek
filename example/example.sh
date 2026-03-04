#!/bin/bash
set -euo pipefail

rm -fr result/
mkdir -p result/

# convert
neotcrseek convert --infile data/control.txt.gz --outfile result/control.tsv
neotcrseek convert --infile data/case.txt.gz --outfile result/case.tsv

# detect
neotcrseek detect --case result/case.tsv --control result/control.tsv --outdir result/ --fc-threshold 300 --case-freq-cutoff 0.0001 --fdr-threshold 1 --control-freq-threshold 0

# plot
Rscript plot_freq_dotplot.R result/expanded_TCRs.txt result/expanded_TCRs.dotplot.png sample_name
