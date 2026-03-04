#!/usr/bin/env python3

import glob
import os
import sys
import pandas as pd

if len(sys.argv) != 3:
    print("Usage: python f1-score_merge.py <base_dir> <output_prefix>")
    sys.exit(1)

base_dir = sys.argv[1].rstrip("/")
out_prefix = sys.argv[2]

patterns = [
    "detect/*/*/expanded_TCRs.eval.txt",
]

records = []

for pattern in patterns:
    search_path = os.path.join(base_dir, pattern)

    for file in glob.glob(search_path):
        parts = file.split(os.sep)

        detect = parts[-4]
        antigen = parts[-3]
        param = parts[-2]

        df = pd.read_csv(file, sep="\t")

        row = df.loc[0]

        records.append([
            detect,
            antigen,
            param,
            int(row["TP"]),
            int(row["FP"]),
            int(row["TN"]),
            int(row["FN"]),
            float(row["Precision"]),
            float(row["Recall"]),
            float(row["F1-score"]),
            float(row["F1-score_weight"]),
        ])

result = pd.DataFrame(
    records,
    columns=[
        "Detect",
        "Antigen",
        "Parameter",
        "TP",
        "FP",
        "TN",
        "FN",
        "Precision",
        "Recall",
        "F1-score",
        "F1-score_weight",
    ],
)

result = result.sort_values(
    by=["Detect", "Antigen", "Parameter"]
)

summary_file = out_prefix + ".summary.tsv"
result.to_csv(summary_file, sep="\t", index=False)

print("Written:")
print(" ", summary_file)

