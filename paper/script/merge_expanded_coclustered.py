#!/usr/bin/env python3

import argparse
import pandas as pd


def to_bool(series):
    """Robust boolean conversion"""
    return series.astype(str).str.lower().isin(
        ["true", "1", "t", "yes"]
    )


def normalize_cdr3aa(series):
    """Normalize CDR3aa strings for safe matching"""
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
    )


def main():
    parser = argparse.ArgumentParser(
        description="Merge expanded TCRs with co-clustered TCRs"
    )
    parser.add_argument(
        "--expanded_tcrs",
        required=True,
        help="Path to expanded_TCRs.txt"
    )
    parser.add_argument(
        "--coclustered_tcrs",
        required=True,
        help="Path to co-clustered_TCRs.txt"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path"
    )

    args = parser.parse_args()

    # ---------- read expanded TCRs ----------
    df = pd.read_csv(args.expanded_tcrs, sep="\t")
    if "cdr3aa" not in df.columns or "Expanded" not in df.columns:
        raise ValueError("expanded_TCRs.txt must contain cdr3aa and Expanded columns")

    df["cdr3aa"] = normalize_cdr3aa(df["cdr3aa"])
    df["Expanded"] = to_bool(df["Expanded"])

    # ---------- read co-clustered TCRs ----------
    df_cc = pd.read_csv(args.coclustered_tcrs, sep="\t")
    if "cdr3aa" not in df_cc.columns:
        raise ValueError("co-clustered_TCRs.txt must contain cdr3aa column")

    df_cc["cdr3aa"] = normalize_cdr3aa(df_cc["cdr3aa"])

    coclustered_set = set(df_cc["cdr3aa"])

    # ---------- annotate ----------
    df["Co-clustered"] = df["cdr3aa"].isin(coclustered_set)

    # ---------- Identified definition ----------
    df["Identified"] = df["Expanded"] | df["Co-clustered"]

    # ---------- write output ----------
    df.to_csv(args.output, sep="\t", index=False)


if __name__ == "__main__":
    main()
