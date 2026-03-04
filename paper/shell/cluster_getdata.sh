#!/bin/bash
set -euo pipefail

workdir="./result"
outdir="$workdir/cluster"
for ag in CMV-pp65 Neo-74 Neo-Mix; do
    mkdir -p "$outdir/$ag/data"
done

para="300_0.0001_1_0"

cat $workdir/detect/CMV-pp65/$para/expanded_TCRs.anno.txt | awk '$3>=1e-4' | awk -F "\t" '{print $2"\t"$3"\t"$4"\t"$14"\t"$18"\t"$19}' > $outdir/CMV-pp65/data/TCR.GIANA.tsv
cat $workdir/detect/Neo-74/$para/expanded_TCRs.anno.txt | awk '$3>=1e-4' | awk -F "\t" '{print $2"\t"$3"\t"$4"\t"$14"\t"$18"\t"$19}' > $outdir/Neo-74/data/TCR.GIANA.tsv
cat $workdir/detect/Neo-Mix/$para/expanded_TCRs.anno.txt | awk '$3>=1e-4' | awk -F "\t" '{print $2"\t"$3"\t"$4"\t"$14"\t"$18"\t"$19}' > $outdir/Neo-Mix/data/TCR.GIANA.tsv

cat $workdir/convert/CMV-pp65/CMV-pp65.tsv | awk '$3>=1e-4' | awk -F "\t" '{print $1"\t"$6"\t"$8"\tNA\tNA\t"$2}' | sed '1d' > $outdir/CMV-pp65/data/TCR.GLIPH.tsv
cat $workdir/convert/Neo-74/Neo-74.tsv | awk '$3>=1e-4' | awk -F "\t" '{print $1"\t"$6"\t"$8"\tNA\tNA\t"$2}' | sed '1d' > $outdir/Neo-74/data/TCR.GLIPH.tsv
cat $workdir/convert/Neo-Mix/Neo-Mix.tsv | awk '$3>=1e-4' | awk -F "\t" '{print $1"\t"$6"\t"$8"\tNA\tNA\t"$2}' | sed '1d' > $outdir/Neo-Mix/data/TCR.GLIPH.tsv

cat $workdir/convert/CMV-pp65/CMV-pp65.tsv | awk '$3>=1e-4' | awk -F "\t" '{print $1"\t"$6"\t"$8"\t"$2"\t"$3}'> $outdir/CMV-pp65/data/TCR.tcrvalid.tsv
cat $workdir/convert/Neo-74/Neo-74.tsv | awk '$3>=1e-4' | awk -F "\t" '{print $1"\t"$6"\t"$8"\t"$2"\t"$3}' > $outdir/Neo-74/data/TCR.tcrvalid.tsv
cat $workdir/convert/Neo-Mix/Neo-Mix.tsv | awk '$3>=1e-4' |awk -F "\t" '{print $1"\t"$6"\t"$8"\t"$2"\t"$3}' > $outdir/Neo-Mix/data/TCR.tcrvalid.tsv


