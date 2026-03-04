#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage:"
    echo "sh run.sh <prop_cutoff> <rate_cutoff>"
    exit 1
fi

prop_cutoff=$1
rate_cutoff=$2

script_dir=$(realpath "./script")

script1="$script_dir/tcrvalid_DBSCAN.py"
script_evaluate="$script_dir/cluster_evaluate_tcrvalid.py"

result_base=$(realpath "$script_dir/../result")
cluster_base="$result_base/cluster"

antigens=(CMV-pp65 Neo-74 Neo-Mix)
para="300_0.0001_1_0"

for antigen in "${antigens[@]}"; do
    workdir="$cluster_base/$antigen"
    outdir="$workdir/TCR-VALID"
    mkdir -p "$outdir"

    cdr3_file="$workdir/data/TCR.tcrvalid.tsv"
    outfile="$outdir/tcrvalid_batch.txt"
    evalfile="${outfile}.eval.txt"

    if [[ ! -f "$cdr3_file" ]]; then
        echo "Skip $antigen (no input)"
        continue
    fi

    if [[ -f "$outfile" ]]; then
        echo "Skip $antigen (tcrvalid exists)"
    else
        echo "Running tcrvalid: $antigen"
        python "$script1" "$cdr3_file" "$outfile"
    fi

    infile1="$result_base/detect/$antigen/$para/expanded_TCRs.anno.txt"
    infile2="$outfile"

    if [[ ! -f "$infile1" || ! -f "$infile2" ]]; then
        echo "Skip evaluate $antigen"
        continue
    fi

    echo "Evaluate $antigen"

    value=3.0
    python "$script_evaluate" \
            "$infile1" \
            "$infile2" \
            "eps_$value" \
            "$prop_cutoff" \
            "$rate_cutoff" \
            >> "$evalfile"

done

echo "All done."

