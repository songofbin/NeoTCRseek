#!/bin/bash
set -euo pipefail

mkdir -p result/convert/{CMV-pp65,Neo-74,Neo-Mix,NC}

# neotcrseek convert --infile data/CMV-pp65/CMV-pp65.txt.gz --outfile result/convert/CMV-pp65/CMV-pp65.tsv
find data/*/*txt.gz -exec bash -c '
  infile="$1"
  outfile="result/convert/$(basename $(dirname "$infile"))/$(basename "${infile%.txt.gz}.tsv")"
  mkdir -p "$(dirname "$outfile")"
  neotcrseek convert --infile "$infile" --outfile "$outfile"
' -- {} \;

