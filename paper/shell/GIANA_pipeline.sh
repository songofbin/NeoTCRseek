#!/bin/bash
set -euo pipefail

if [ "$#" -ne 4 ]; then
    echo "Usage:"
    echo "sh 01GIANA_pipeline.sh <GIANA:threshold> <GIANA:threshold_score> <Filter:prop_cutoff> <Filter:rate_cutoff>"
    exit 1
fi

threshold=$1
threshold_score=$2
prop_cutoff=$3
rate_cutoff=$4

outsuffix="${threshold}_${threshold_score}"

script="./tool/GIANA/GIANA4.1.py"
script_evaluate="./script/cluster_evaluate.py"
result_base="./result"

antigens=(CMV-pp65 Neo-74 Neo-Mix)
para="300_0.0001_1_0"

MAX_JOBS=4

wait_jobs() {
    while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
        sleep 1
    done
}

echo "=== Step 1: Running GIANA ==="

for antigen in "${antigens[@]}"; do
    wait_jobs

    (
        infile="$result_base/cluster/$antigen/data/TCR.GIANA.tsv"
        outdir="$result_base/cluster/$antigen/GIANA"
        outfile="$outdir/GIANA_${outsuffix}.txt"

        [[ -e "$infile" ]] || { echo "Skip $antigen (no input): $infile"; exit 0; }

        mkdir -p "$outdir"

        if [[ -e "$outfile" ]]; then
            echo "Skip $antigen (exists)"
            exit 0
        fi

        echo "Processing $antigen"

        python "$script" \
            -f "$infile" \
            -O "$outfile" \
            -t "$threshold" \
            -S "$threshold_score"
    ) &
done

wait
echo "GIANA finished."

echo "=== Step 2: Evaluate results ==="

mergedir="$result_base/cluster/GIANA"
mkdir -p "$mergedir"

outfile="$mergedir/merge_${outsuffix}_${prop_cutoff}_${rate_cutoff}.txt"
: > "$outfile"

for antigen in "${antigens[@]}"; do
    wait_jobs

    (
        infile1="$result_base/detect/$antigen/$para/expanded_TCRs.anno.txt"
        infile2="$result_base/cluster/$antigen/GIANA/GIANA_${outsuffix}.txt"

        if [[ ! -e "$infile1" || ! -e "$infile2" ]]; then
            echo "Skip $antigen (missing input)"
            exit 0
        fi

        tmpfile=$(mktemp)

        echo "Evaluate $antigen"

        python "$script_evaluate" \
            "$infile1" \
            "$infile2" \
            "$prop_cutoff" \
            "$rate_cutoff" \
            > "$tmpfile"

        cat "$tmpfile" >> "$outfile"
        rm "$tmpfile"
    ) &
done

wait

echo "Evaluate result written to:"
echo "$outfile"

