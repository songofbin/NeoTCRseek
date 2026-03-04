#!/bin/bash
set -euo pipefail

cluster_purity=0.5
FC_threshold=100

bash shell/cluster_getdata.sh

# GIANA
export PYTHONPATH=""
conda activate GIANA
bash shell/GIANA_pipeline.sh 9 1 $cluster_purity $FC_threshold
conda deactivate

# GLIPH2
bash shell/GLIPH2_pipeline.sh 0.01 2 8 $cluster_purity $FC_threshold

# TCR-VALID
export PYTHONPATH=""
conda activate tcrvalid
bash shell/TCR-VALID_pipeline.sh $cluster_purity $FC_threshold
conda deactivate

# result
dir="./result/cluster/"

for f in $dir/*/GIANA/GIANA_9_1_score.tsv.unique.txt; do
    dir1=$(dirname "$f")
    ln -sf GIANA_9_1_score.tsv.unique.txt "$dir1/unique.txt"
done

for f in $dir/*/GLIPH2/GLIPH_cluster_0.01_2_8.format_score.tsv.unique.txt; do
    dir1=$(dirname "$f")
    ln -sf GLIPH_cluster_0.01_2_8.format_score.tsv.unique.txt "$dir1/unique.txt"
done

for f in $dir/*/TCR-VALID/tcrvalid_batch_eps_3.0.tsv.unique.txt; do
    dir1=$(dirname "$f")
    ln -sf tcrvalid_batch_eps_3.0.tsv.unique.txt "$dir1/unique.txt"
done

python script/merge_cluster_predictions.py --input_dir result/cluster/CMV-pp65 --output result/cluster/CMV-pp65/co-clustered_TCRs.txt
python script/merge_cluster_predictions.py --input_dir result/cluster/Neo-74 --output result/cluster/Neo-74/co-clustered_TCRs.txt
