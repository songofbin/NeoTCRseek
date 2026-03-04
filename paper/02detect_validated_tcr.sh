#!/bin/bash
set -euo pipefail

mkdir -p result/validate/{CMV-pp65,Neo-74,Neo-Mix}

fre_cutoff_list=(1e-3 1e-4 1e-5)

for fre in "${fre_cutoff_list[@]}"; do

    python script/detect_enriched_tcr.py \
        --unsorted_file result/convert/CMV-pp65/CMV-pp65.tsv \
        --positive_file result/convert/CMV-pp65/CD137p.tsv \
        --negative_file result/convert/CMV-pp65/CD137n.tsv \
        --fold1 1 --fold2 1 \
        --freq_cutoff ${fre} \
        --output_file result/validate/CMV-pp65/CD137.enriched_tcr.${fre}.tsv

    python script/detect_enriched_tcr.py \
        --unsorted_file result/convert/CMV-pp65/CMV-pp65.tsv \
        --positive_file result/convert/CMV-pp65/Tetramer1p.tsv \
        --negative_file result/convert/CMV-pp65/Tetramer1n.tsv \
        --fold1 1 --fold2 1 \
        --freq_cutoff ${fre} \
        --output_file result/validate/CMV-pp65/Tetramer1.enriched_tcr.${fre}.tsv

    python script/detect_enriched_tcr.py \
        --unsorted_file result/convert/CMV-pp65/CMV-pp65.tsv \
        --positive_file result/convert/CMV-pp65/Tetramer2p.tsv \
        --negative_file result/convert/CMV-pp65/Tetramer2n.tsv \
        --fold1 1 --fold2 1 \
        --freq_cutoff ${fre} \
        --output_file result/validate/CMV-pp65/Tetramer2.enriched_tcr.${fre}.tsv

    python script/plot_venn_tcr.py \
    	-i result/validate/CMV-pp65/CD137.enriched_tcr.${fre}.cdr3aa.list \
        result/validate/CMV-pp65/Tetramer1.enriched_tcr.${fre}.cdr3aa.list \
        result/validate/CMV-pp65/Tetramer2.enriched_tcr.${fre}.cdr3aa.list \
    	--labels CD137 Tetramer1 Tetramer2 \
    	-o result/validate/CMV-pp65/venn.enriched_tcr.${fre}.png

    python script/detect_validated_tcr.py \
        -i \
        result/validate/CMV-pp65/CD137.enriched_tcr.${fre}.tsv \
        result/validate/CMV-pp65/Tetramer1.enriched_tcr.${fre}.tsv \
        result/validate/CMV-pp65/Tetramer2.enriched_tcr.${fre}.tsv \
        -o result/validate/CMV-pp65/validated_tcr.${fre}.tsv

done

for fre in "${fre_cutoff_list[@]}"; do

    python script/detect_enriched_tcr.py \
        --unsorted_file result/convert/Neo-74/Neo-74.tsv \
        --positive_file result/convert/Neo-74/CD137p.tsv \
        --negative_file result/convert/Neo-74/CD137n.tsv \
        --fold1 5 --fold2 5 \
        --freq_cutoff ${fre} \
        --output_file result/validate/Neo-74/CD137.enriched_tcr.${fre}.tsv

    python script/detect_enriched_tcr.py \
        --unsorted_file result/convert/Neo-74/Neo-74.tsv \
        --positive_file result/convert/Neo-74/Tetramer1p.tsv \
        --negative_file result/convert/Neo-74/Tetramer1n.tsv \
        --fold1 5 --fold2 5 \
        --freq_cutoff ${fre} \
        --output_file result/validate/Neo-74/Tetramer1.enriched_tcr.${fre}.tsv

    python script/detect_enriched_tcr.py \
        --unsorted_file result/convert/Neo-74/Neo-74.tsv \
        --positive_file result/convert/Neo-74/Tetramer2p.tsv \
        --negative_file result/convert/Neo-74/Tetramer2n.tsv \
        --fold1 1 --fold2 1 \
        --freq_cutoff ${fre} \
        --output_file result/validate/Neo-74/Tetramer2.enriched_tcr.${fre}.tsv

    python script/plot_venn_tcr.py \
    	-i result/validate/Neo-74/CD137.enriched_tcr.${fre}.cdr3aa.list \
        result/validate/Neo-74/Tetramer1.enriched_tcr.${fre}.cdr3aa.list \
        result/validate/Neo-74/Tetramer2.enriched_tcr.${fre}.cdr3aa.list \
    	--labels CD137 Tetramer1 Tetramer2 \
    	-o result/validate/Neo-74/venn.enriched_tcr.${fre}.png

    python script/detect_validated_tcr.py \
        -i \
        result/validate/Neo-74/CD137.enriched_tcr.${fre}.tsv \
        result/validate/Neo-74/Tetramer1.enriched_tcr.${fre}.tsv \
        result/validate/Neo-74/Tetramer2.enriched_tcr.${fre}.tsv \
        -o result/validate/Neo-74/validated_tcr.${fre}.tsv

done


for fre in "${fre_cutoff_list[@]}"; do

    python script/detect_enriched_tcr.py \
        --unsorted_file result/convert/Neo-Mix/Neo-Mix.tsv \
        --positive_file result/convert/Neo-Mix/CD137p.tsv \
        --negative_file result/convert/Neo-Mix/CD137n.tsv \
        --fold1 5 --fold2 5 \
        --freq_cutoff ${fre} \
        --output_file result/validate/Neo-Mix/CD137.enriched_tcr.${fre}.tsv

    python script/detect_enriched_tcr.py \
        --unsorted_file result/convert/Neo-Mix/Neo-Mix.tsv \
        --positive_file result/convert/Neo-Mix/Tetramer2p.tsv \
        --negative_file result/convert/Neo-Mix/Tetramer2n.tsv \
        --fold1 1 --fold2 1 \
        --freq_cutoff ${fre} \
        --output_file result/validate/Neo-Mix/Tetramer2.enriched_tcr.${fre}.tsv

    python script/plot_venn_tcr.py \
    	-i result/validate/Neo-Mix/CD137.enriched_tcr.${fre}.cdr3aa.list \
        result/validate/Neo-Mix/Tetramer2.enriched_tcr.${fre}.cdr3aa.list \
    	--labels CD137 Tetramer2 \
    	-o result/validate/Neo-Mix/venn.enriched_tcr.${fre}.png

    python script/detect_validated_tcr.py \
        -i \
        result/validate/Neo-Mix/CD137.enriched_tcr.${fre}.tsv \
        result/validate/Neo-Mix/Tetramer2.enriched_tcr.${fre}.tsv \
        -o result/validate/Neo-Mix/validated_tcr.${fre}.tsv

done
