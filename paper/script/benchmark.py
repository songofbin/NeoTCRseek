#!/usr/bin/env python3

import argparse
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from pathlib import Path
import re

def to_bool(series):
    return series.astype(str).str.lower().isin(
        ["true", "yes"]
    )

def annotate_true_tcr(expanded_tcr_file, true_tcr_file, output_file):
    df = pd.read_csv(expanded_tcr_file, sep="\t")
    df_true = pd.read_csv(true_tcr_file, sep="\t")

    true_cdr3aa_set = set(df_true["cdr3aa"].dropna())
    df["TrueTCR"] = df["cdr3aa"].isin(true_cdr3aa_set)

    df.to_csv(output_file, sep="\t", index=False)
    print(f"Annotated file saved to {output_file}")

    return df

def evaluate(df, output_file, eval_col="Identified", freq_type="freq_c"):
    """
      Calculated the following metrics based on the eval_col (detection) and TrueTCR (ground truth) columns
      TP, FP, TN, FN
      Precision, Recall, F1-score
      F1-score_weight (frequency weighted)
    """

    for col in [eval_col, "TrueTCR"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    if freq_type not in df.columns:
        raise ValueError(f"Missing frequency column: {freq_type}")

    y_true = to_bool(df["TrueTCR"])
    y_pred = to_bool(df[eval_col])

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[False, True]
    ).ravel()

    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    # ---------- weighted F1 ----------
    weights = df[freq_type].fillna(0)

    f1_weight = f1_score(
        y_true,
        y_pred,
        sample_weight=weights,
        zero_division=0,
    )

    with open(output_file, "w") as f:
        f.write(
            "TP\tFP\tTN\tFN\tPrecision\tRecall\tF1-score\tF1-score_weight\n"
        )
        f.write(
            f"{tp}\t{fp}\t{tn}\t{fn}\t"
            f"{precision:.4f}\t{recall:.4f}\t{f1:.4f}\t"
            f"{f1_weight:.4f}\n"
        )

    print(f"Evaluation metrics saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Annotate identified TCRs with TrueTCR label and evaluate performance."
    )

    parser.add_argument(
        "--identified_tcrs",
        required=True,
        help="Identified TCR table",
    )

    parser.add_argument(
        "--true_tcrs",
        required=True,
        help="TrueTCR list",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output benchmarking",
    )

    parser.add_argument(
        "--eval_col",
        default="Identified",
        help="Evaluate column name (default: Identified )",
    )

    args = parser.parse_args()

    output_data_file = re.sub(r"\.eval\.txt$", ".anno.txt", args.output)

    df = annotate_true_tcr(
        expanded_tcr_file=args.identified_tcrs,
        true_tcr_file=args.true_tcrs,
        output_file=output_data_file,
    )

    evaluate(df, args.output, eval_col=args.eval_col)


if __name__ == "__main__":
    main()
