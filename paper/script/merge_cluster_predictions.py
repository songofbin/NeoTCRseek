#!/usr/bin/env python3

import argparse
import pandas as pd
from pathlib import Path
from collections import defaultdict


def main():
    parser = argparse.ArgumentParser(
        description="Merge unique TCR predictions from multiple clustering methods"
    )
    parser.add_argument(
        "--input_dir",
        required=True,
        help="Directory containing method subdirectories (each with unique.txt)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output merged file",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    method_map = defaultdict(list)

    # iterate over method directories
    for method_dir in input_dir.iterdir():
        if not method_dir.is_dir():
            continue

        method_name = method_dir.name
        unique_file = method_dir / "unique.txt"

        if not unique_file.exists():
            continue

        df = pd.read_csv(unique_file, sep="\t")

        # basic sanity check
        if not {"cdr3aa", "Detected_check"}.issubset(df.columns):
            raise ValueError(f"Missing required columns in {unique_file}")

        # keep only Detected_check == True
        df = df[df["Detected_check"].astype(str).str.lower() == "true"]

        for cdr3aa in df["cdr3aa"].dropna():
            method_map[cdr3aa].append(method_name)

    # build output dataframe
    out_df = pd.DataFrame(
        [
            {
                "cdr3aa": cdr3aa,
                "Predicted by": ", ".join(sorted(methods)),
            }
            for cdr3aa, methods in method_map.items()
        ]
    ).sort_values("cdr3aa")

    out_df.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
