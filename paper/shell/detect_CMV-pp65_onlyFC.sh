#!/bin/bash
set -euo pipefail

case_file="result/convert/CMV-pp65/CMV-pp65.tsv"
control_file="result/convert/NC/control.tsv"

case_freq_cutoff=0.0001
fdr_threshold=1
control_freq_threshold=-1

out_root="result/detect/CMV-pp65"

for FC in 100 200 300; do
    out_dir="${out_root}/${FC}_${case_freq_cutoff}_${fdr_threshold}_${control_freq_threshold}"
    mkdir -p "$out_dir"

    neotcrseek detect \
        --case "$case_file" \
        --control "$control_file" \
        --fc-threshold "$FC" \
        --case-freq-cutoff "$case_freq_cutoff" \
        --fdr-threshold "$fdr_threshold" \
        --control-freq-threshold "$control_freq_threshold" \
        --outdir "$out_dir"
done

