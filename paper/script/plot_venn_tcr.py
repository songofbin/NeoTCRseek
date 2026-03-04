#!/usr/bin/env python3

import pandas as pd
import argparse
import sys
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# -----------------------------
# Import local pyvenn module
# -----------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
import venn


# -----------------------------
# Read input
# -----------------------------
def read_cdr3_set(file):
    df = pd.read_csv(file, sep="\t", usecols=["cdr3aa"])
    return set(df["cdr3aa"].dropna())


# -----------------------------
# Journal-ready style
# -----------------------------
def setup_style():
    sns.set_style("white")

    mpl.rcParams["font.family"] = "Arial"
    mpl.rcParams["font.size"] = 30
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42
    mpl.rcParams["axes.linewidth"] = 1.5


# -----------------------------
# Format text appearance
# -----------------------------
def format_ax_text(ax):
    for text in ax.texts:
        if text:
            text.set_fontsize(30)
            text.set_fontweight("bold")


# -----------------------------
# Main
# -----------------------------
def main():

    parser = argparse.ArgumentParser(
        description="Journal-ready Venn plot (2–4 sets) using pyvenn"
    )

    parser.add_argument(
        "-i", "--input",
        nargs="+",
        required=True,
        help="Input files (2–4 files, must contain column 'cdr3aa')"
    )

    parser.add_argument(
        "--labels",
        nargs="+",
        required=True,
        help="Circle labels (must match number of input files)"
    )

    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output figure (png/pdf/svg)"
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=600
    )

    parser.add_argument(
        "--transparent",
        action="store_true"
    )

    args = parser.parse_args()

    n = len(args.input)

    if n < 2 or n > 4:
        raise ValueError("Only 2–4 input files supported.")

    if len(args.labels) != n:
        raise ValueError("Number of labels must equal number of input files.")

    setup_style()

    # Read sets
    sets = [read_cdr3_set(f) for f in args.input]

    # Generate pyvenn labels
    labels = venn.get_labels(sets, fill=["number"])

    # Plot
    plt.figure(figsize=(8, 8))

    if n == 2:
        fig, ax = venn.venn2(labels, names=args.labels)

    elif n == 3:
        fig, ax = venn.venn3(labels, names=args.labels)

    elif n == 4:
        fig, ax = venn.venn4(labels, names=args.labels)

    else:
        raise ValueError("Only 2–4 sets supported.")

    # Remove legend if exists
    if hasattr(ax, "legend_") and ax.legend_:
        ax.legend_.remove()

    # Format fonts
    format_ax_text(ax)

    plt.tight_layout()
    plt.savefig(
        args.output,
        dpi=args.dpi,
        bbox_inches="tight",
        transparent=args.transparent
    )
    plt.close()


if __name__ == "__main__":
    main()
