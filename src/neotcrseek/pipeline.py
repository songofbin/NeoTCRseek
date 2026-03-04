#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import pandas as pd
import copy
import logging
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests

def read_table_auto(infile):
    compression = "gzip" if str(infile).endswith(".gz") else None
    df = pd.read_csv(infile, sep="\t", compression=compression)
    return df

def convert_VDJtools(infile):
    df = read_table_auto(infile)

    cols = ["count", "freq", "cdr3nt", "cdr3aa", "v", "d", "j"]
    df = df[cols].copy()

    # aggregate main statistics
    agg = (
        df.groupby("cdr3aa")
        .agg(
            count=("count", "sum"),
            freq=("freq", "sum"),
            convergence=("cdr3nt", "count"),
            v=("v", "first"),
            d=("d", "first"),
            j=("j", "first"),
        )
        .reset_index()
    )

    # total count
    agg["countSum"] = agg["count"].sum()

    # unique vdj combinations
    df["vdj"] = df["v"] + "_" + df["d"] + "_" + df["j"]

    vdj_unique = (
        df.groupby("cdr3aa")["vdj"]
        .apply(lambda x: ",".join(sorted(set(x))))
        .reset_index(name="vdj")
    )

    # merge vdj info
    result = agg.merge(vdj_unique, on="cdr3aa", how="left")

    # final ordering
    result = result.sort_values("count", ascending=False).reset_index(drop=True)

    # reorder columns
    result = result[
        ["cdr3aa", "count", "freq", "convergence", "countSum", "v", "d", "j", "vdj"]
    ]

    return result

def load_tcr_table(file):

    """
    Load a single TCR TSV file and standardize required columns.
    """

    if not file.exists():
        logging.error(f"TCR data file not found: {file}")
        sys.exit(1)

    df = pd.read_csv(file, sep="\t")

    needed_cols = ["cdr3aa", "v", "j", "count", "freq", "convergence", "countSum"]
    missing = set(needed_cols) - set(df.columns)
    if missing:
        logging.error(f"Missing required columns in {file}: {missing}")
        sys.exit(1)

    df = df.loc[:, needed_cols].copy()
    df.insert(0, "ID", range(1, len(df) + 1), True)

    return df
    
def culture_expand(
    case,
    control,
    freq_c_cutoff=1e-4,
    fc_threshold=300,
    FDR_threshold=1,
    freq_b_threshold=0,
):
    """
    Detect TCR clonotypes expanded in cultured samples relative to control.

    Expanded clonotypes satisfy:

        1. freq_c >= freq_c_cutoff
        2. FC >= fc_threshold
        3. FDR < FDR_threshold
        4. freq_b > freq_b_threshold

    Parameters
    ----------
    case : pandas.DataFrame
    control : pandas.DataFrame

    freq_c_cutoff : float
        Detection limit in the case sample. Clonotypes with
        freq_c below this cutoff are considered undetected and excluded
        from downstream analysis.

    fc_threshold : float
        Fold-change filtering threshold. Clonotypes with FC below this
        threshold are not considered expanded.

    FDR_threshold : float
        Statistical filtering threshold from Fisher's exact test.
        Clonotypes with FDR greater than or equal to this threshold
        are excluded.

    freq_b_threshold : float
        Filtering threshold in the control sample. Clonotypes with
        control frequency not exceeding this threshold are removed.


    Returns
    -------
    df_result : pandas.DataFrame
    df_stat : pandas.DataFrame
    """

    # ---------- merge ----------
    df_merge = pd.merge(
        case,
        control,
        on="cdr3aa",
        how="outer",
        suffixes=("_c", "_b"),
    )

    # ---------- case frequency filter ----------
    df_merge = df_merge.loc[df_merge["freq_c"] >= freq_c_cutoff]

    # ---------- control frequency handling ----------
    value_min = 1e-6

    df_merge["freq_b_raw"] = df_merge["freq_b"]
    df_merge["freq_b"] = df_merge["freq_b"].fillna(value_min)
    df_merge.loc[df_merge["freq_b"] < value_min, "freq_b"] = value_min

    # ---------- countSum filling ----------
    max_case = case["countSum"].max()
    max_control = control["countSum"].max()

    df_merge["countSum_c"] = df_merge["countSum_c"].fillna(max_case)
    df_merge["countSum_b"] = df_merge["countSum_b"].fillna(max_control)

    df_merge = df_merge.fillna(0)

    # ---------- compute fold change ----------
    df_merge["FC"] = df_merge["freq_c"] / df_merge["freq_b"]
    df_merge["FC"] = df_merge["FC"].round(2)

    # ---------- statistical test ----------
    df_result = run_fisher_test_row(df_merge)

    # ---------- filtering ----------
    df_keep = df_result.loc[
        (df_result["FC"] >= fc_threshold)
        & (df_result["FDR"] < FDR_threshold)
        & (df_result["freq_b_raw"] > freq_b_threshold)
    ]

    df_result["Expanded"] = df_result["cdr3aa"].isin(
        set(df_keep["cdr3aa"])
    )

    # ---------- sorting ----------
    df_result = df_result.sort_values(by="freq_c", ascending=False)

    # ---------- rename/drop ----------
    df_result = (
        df_result.rename(
            columns={
                "ID_c": "ID",
                "v_c": "v",
                "j_c": "j",
            }
        )
        .drop(columns=["ID_b", "v_b", "j_b"], errors="ignore")
    )

    # ---------- integer columns ----------
    cols_to_convert = [
        "ID",
        "count_c",
        "convergence_c",
        "countSum_c",
        "count_b",
        "convergence_b",
        "countSum_b",
    ]

    df_result[cols_to_convert] = df_result[cols_to_convert].astype("Int64")

    # ---------- statistics ----------
    num_case = case.shape[0]
    num_control = control.shape[0]
    num_expand = df_keep.shape[0]

    freq_case = round(df_keep["freq_c"].sum(), 4)
    freq_control = round(df_keep["freq_b_raw"].sum(), 4)

    filter_cutoff = [
        fc_threshold,
        freq_c_cutoff,
        FDR_threshold,
        freq_b_threshold,
    ]
    filter_info = "_".join(map(str, filter_cutoff))

    df_stat = pd.DataFrame(
        [[
            filter_info,
            num_case,
            num_control,
            num_expand,
            freq_case,
            freq_control,
        ]],
        columns=[
            "filter_info",
            "num_case",
            "num_control",
            "num_expand",
            "freq_case",
            "freq_control",
        ],
    )

    return df_result, df_stat
    
def run_fisher_test_row(df_merge):
    df_result = df_merge.copy()

    stats = df_result.apply(fisher_test_row, axis=1)
    stats["OR"] = stats["OR"].round(2)
    stats["FDR"] = fdr_correction(stats["Pvalue"])

    return pd.concat([df_result, stats], axis=1)

def fisher_test_row(row, pseudocount=1):
    a = row.get("count_c", 0) + pseudocount
    b = (row.get("countSum_c", 0) - row.get("count_c", 0)) + pseudocount
    c = row.get("count_b", 0) + pseudocount
    d = (row.get("countSum_b", 0) - row.get("count_b", 0)) + pseudocount

    table = [[a, b], [c, d]]

    or_value, p_value = fisher_exact(table, alternative="greater")

    return pd.Series({
        "OR": or_value,
        "Pvalue": p_value
    })

def fdr_correction(pvals):
    _, fdrs, _, _ = multipletests(pvals, method='fdr_bh')
    return fdrs
