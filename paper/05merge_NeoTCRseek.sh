# NeoTCRseek
para="300_0.0001_1_0"

python script/merge_expanded_coclustered.py --expanded_tcrs result/detect/CMV-pp65/$para/expanded_TCRs.txt --coclustered_tcrs result/cluster/CMV-pp65/co-clustered_TCRs.txt --output result/detect/CMV-pp65/$para/identified_TCRs.txt
python script/benchmark.py --identified_tcrs result/detect/CMV-pp65/$para/identified_TCRs.txt --true_tcrs result/validate/CMV-pp65/validated_tcr.1e-5.tsv --output result/detect/CMV-pp65/$para/identified_TCRs.eval.txt --eval_col Identified

python script/merge_expanded_coclustered.py --expanded_tcrs result/detect/Neo-74/$para/expanded_TCRs.txt --coclustered_tcrs result/cluster/Neo-74/co-clustered_TCRs.txt --output result/detect/Neo-74/$para/identified_TCRs.txt
python script/benchmark.py --identified_tcrs result/detect/Neo-74/$para/identified_TCRs.txt --true_tcrs result/validate/Neo-74/validated_tcr.1e-4.tsv --output result/detect/Neo-74/$para/identified_TCRs.eval.txt --eval_col Identified

