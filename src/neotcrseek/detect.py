import logging
from pathlib import Path
import pandas as pd

from .pipeline import load_tcr_table
from .pipeline import culture_expand


def run_detect(
    case_file: Path,
    control_file: Path,
    fc_threshold: float,
    freq_c_cutoff: float,
    FDR_threshold: float,
    freq_b_threshold: float,
    out_dir: Path,
):
    outpath = out_dir
    outpath.mkdir(parents=True, exist_ok=True)

    logging.info("Loading case sample...")
    df_case = load_tcr_table(case_file)

    logging.info("Loading control sample...")
    df_control = load_tcr_table(control_file)

    logging.info("Detecting expanded TCR clonotypes...")

    df_expanded, df_stat = culture_expand(
        df_case,
        df_control,
        freq_c_cutoff=freq_c_cutoff,
        fc_threshold=fc_threshold,
        FDR_threshold=FDR_threshold,
        freq_b_threshold=freq_b_threshold,
    )

    df_expanded.to_csv(
        outpath / "expanded_TCRs.txt",
        sep="\t",
        index=False,
    )

    df_stat.to_csv(
        outpath / "expanded_TCRs.stat.txt",
        sep="\t",
        index=False,
    )

    logging.info("Detection finished successfully.")
