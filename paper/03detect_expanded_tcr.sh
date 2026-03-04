#!/bin/bash
set -euo pipefail

# initial detection  
base_para="100_0.0001_1_-1"
neotcrseek detect --case result/convert/CMV-pp65/CMV-pp65.tsv --control result/convert/NC/control.tsv --fc-threshold 100 --case-freq-cutoff 0.0001 --fdr-threshold 1 --control-freq-threshold -1 --outdir result/detect/CMV-pp65/$base_para
neotcrseek detect --case result/convert/Neo-74/Neo-74.tsv --control result/convert/NC/control.tsv --fc-threshold 100 --case-freq-cutoff 0.0001 --fdr-threshold 1 --control-freq-threshold -1 --outdir result/detect/Neo-74/$base_para
neotcrseek detect --case result/convert/Neo-Mix/Neo-Mix.tsv --control result/convert/NC/control.tsv --fc-threshold 100 --case-freq-cutoff 0.0001 --fdr-threshold 1 --control-freq-threshold -1 --outdir result/detect/Neo-Mix/$base_para

bash shell/detect_CMV-pp65_onlyFC.sh
bash shell/detect_CMV-pp65_FC-NC0.sh

# final detection
para="300_0.0001_1_0"
neotcrseek detect --case result/convert/CMV-pp65/CMV-pp65.tsv --control result/convert/NC/control.tsv --fc-threshold 300 --case-freq-cutoff 0.0001 --fdr-threshold 1 --control-freq-threshold 0 --outdir result/detect/CMV-pp65/$para
neotcrseek detect --case result/convert/Neo-74/Neo-74.tsv --control result/convert/NC/control.tsv --fc-threshold 300 --case-freq-cutoff 0.0001 --fdr-threshold 1 --control-freq-threshold 0 --outdir result/detect/Neo-74/$para
neotcrseek detect --case result/convert/Neo-Mix/Neo-Mix.tsv --control result/convert/NC/control.tsv --fc-threshold 300 --case-freq-cutoff 0.0001 --fdr-threshold 1 --control-freq-threshold 0 --outdir result/detect/Neo-Mix/$para

# benchmarking
for f in result/detect/CMV-pp65/*/expanded_TCRs.txt; do python script/benchmark.py --identified_tcrs "$f" --true_tcrs result/validate/CMV-pp65/validated_tcr.1e-5.tsv --output "${f%.txt}.eval.txt" --eval_col Expanded; done
for f in result/detect/Neo-74/*/expanded_TCRs.txt; do python script/benchmark.py --identified_tcrs "$f" --true_tcrs result/validate/Neo-74/validated_tcr.1e-4.tsv --output "${f%.txt}.eval.txt" --eval_col Expanded; done
for f in result/detect/Neo-Mix/*/expanded_TCRs.txt; do python script/benchmark.py --identified_tcrs "$f" --true_tcrs result/validate/Neo-Mix/validated_tcr.1e-4.tsv --output "${f%.txt}.eval.txt" --eval_col Expanded; done
python script/f1-score_merge.py result/ result/detect/F1_result

# plot
Rscript script/plot_freq_dotplot_ExpandedTCR.R result/detect/CMV-pp65/$para/expanded_TCRs.anno.txt result/detect/CMV-pp65/$para/plot_freq_dotplot_ExpandedTCR.png CMV-T
Rscript script/plot_freq_dotplot_ExpandedTCR.R result/detect/Neo-74/$para/expanded_TCRs.anno.txt result/detect/Neo-74/$para/plot_freq_dotplot_ExpandedTCR.png Neo-T
Rscript script/plot_freq_dotplot_ExpandedTCR.R result/detect/Neo-Mix/$para/expanded_TCRs.anno.txt result/detect/Neo-Mix/$para/plot_freq_dotplot_ExpandedTCR.png Neo-T
