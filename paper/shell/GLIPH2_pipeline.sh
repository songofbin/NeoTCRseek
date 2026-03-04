#!/bin/bash
set -euo pipefail

if [ "$#" -ne 5 ]; then
    echo "Usage:"
    echo "sh 01GLIPH_pipeline.sh <local_min_pvalue> <kmer_min_depth> <local_min_OVE> <prop_cutoff> <rate_cutoff>"
    exit 1
fi

local_min_pvalue=$1
kmer_min_depth=$2
local_min_OVE=$3
prop_cutoff=$4
rate_cutoff=$5

outsuffix="${local_min_pvalue}_${kmer_min_depth}_${local_min_OVE}"

script_dir=$(realpath "./script")
tool_dir="$(realpath "./tool")"

script1="$tool_dir/gliph2/irtools.centos"
script2=$(realpath "./script/gliph2_result_reformat.py")
script_evaluate=$(realpath "./script/cluster_evaluate.py")

result_base=$(realpath "./result")
cluster_base="$result_base/cluster"

antigens=(CMV-pp65 Neo-74 Neo-Mix)
para="300_0.0001_1_0"

MAX_JOBS=4

wait_jobs() {
    while (( $(jobs -r | wc -l) >= MAX_JOBS )); do
        sleep 1
    done
}

########################################
# Step 1: GLIPH clustering
########################################
echo "=== Step 1: Running GLIPH ==="

for antigen in "${antigens[@]}"; do
    wait_jobs

    (
        workdir="$cluster_base/$antigen"
        outdir="$workdir/GLIPH2"
        cfg="$outdir/GLIPH_${outsuffix}.cfg"
        outfile="$outdir/GLIPH_cluster_${outsuffix}.txt"

        cdr3_file="$workdir/data/TCR.GLIPH.tsv"

        [[ -e "$cdr3_file" ]] || { echo "Skip $antigen (no input)"; exit 0; }

        if [[ -e "$outfile" ]]; then
            echo "Skip $antigen (exists)"
            exit 0
        fi

        mkdir -p "$outdir" "$workdir/data"

        ########################################
        # 生成 GLIPH.cfg
        ########################################
        cat > "$cfg" <<EOF
out_prefix=GLIPH
cdr3_file=$cdr3_file
refer_file=$tool_dir/gliph2/refer_file/human_v2.0/ref_CD8_v2.0.fa
v_usage_freq_file=$tool_dir/gliph2/refer_file/human_v2.0/ref_V_CD8_v2.0.txt
cdr3_length_freq_file=$tool_dir/gliph2/refer_file/human_v2.0/ref_L_CD8_v2.0.txt
local_min_pvalue=$local_min_pvalue
p_depth=10000
global_convergence_cutoff=1
simulation_depth=1000
kmer_min_depth=$kmer_min_depth
local_min_OVE=$local_min_OVE
algorithm=GLIPH2
all_aa_interchangeable=1
EOF

        echo "Running GLIPH: $antigen"

        tmpdir="./tmp_${antigen}_$$_$RANDOM"
        mkdir "$tmpdir"

        (
            cd "$tmpdir"
            "$script1" -c "$cfg"
            mv GLIPH_cluster.txt "$outfile" 2>/dev/null || true
        )

        rm -rf "$tmpdir"

        python "$script2" \
            "$outfile" \
            "$outdir/GLIPH_cluster_${outsuffix}.format.txt"

        echo "Finished $antigen"
    ) &
done

wait
echo "GLIPH finished."

########################################
# Step 2: Evaluate
########################################
echo "=== Step 2: Evaluate results ==="

mergedir="$cluster_base/GLIPH"
mkdir -p "$mergedir"

outfile="$mergedir/merge_${outsuffix}_${prop_cutoff}_${rate_cutoff}.txt"
tmpmerge="$mergedir/.merge_tmp_$$_$RANDOM"
mkdir "$tmpmerge"

for antigen in "${antigens[@]}"; do
    wait_jobs

    (
        infile1="$result_base/detect/$antigen/$para/expanded_TCRs.anno.txt"
        infile2="$cluster_base/$antigen/GLIPH2/GLIPH_cluster_${outsuffix}.format.txt"

        [[ -e "$infile1" && -e "$infile2" ]] || { echo "Skip $antigen"; exit 0; }

        echo "Evaluate $antigen"

        python "$script_evaluate" \
            "$infile1" \
            "$infile2" \
            "$prop_cutoff" \
            "$rate_cutoff" \
            > "$tmpmerge/$antigen.txt"
    ) &
done

wait

: > "$outfile"
cat "$tmpmerge"/*.txt >> "$outfile" 2>/dev/null || true
rm -rf "$tmpmerge"

echo "Evaluate result written to:"
echo "$outfile"

