import argparse
import logging
from pathlib import Path

from . import __version__
from .detect import run_detect
from .convert import run_convert


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    parser = argparse.ArgumentParser(
        prog="neotcrseek",
        description=(
            "NeoTCRseek: detection of expanded neoantigen-specific "
            "TCR clonotypes"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"neotcrseek {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # -------- detect command --------
    detect = subparsers.add_parser(
        "detect",
        help="Detect expanded TCR clonotypes from case/control samples",
    )

    detect.add_argument("--case", required=True, type=Path)
    detect.add_argument("--control", required=True, type=Path)
    detect.add_argument("--outdir", required=True, type=Path)

    # ---------- thresholds ----------
    detect.add_argument(
        "--fc-threshold",
        type=float,
        default=300,
        help="Fold-change threshold (default: 300)"
    )

    detect.add_argument(
        "--case-freq-cutoff",
        type=float,
        default=1e-4,
        help="Frequency cutof in case sample (default: 1e-4)"
    )

    detect.add_argument(
        "--fdr-threshold",
        type=float,
        default=1,
        help="FDR threshold from Fisher test (default: 1)"
    )

    detect.add_argument(
        "--control-freq-threshold",
        type=float,
        default=0,
        help=(
            "Minimum control frequency (default: 0); -1 disables filtering"
        ),
    )

    # -------- convert command --------
    convert = subparsers.add_parser(
        "convert",
        help="Convert VDJtools format to NeoTCRseek format",
    )

    convert.add_argument(
        "--infile",
        required=True,
        type=Path,
        help="Input TCR TSV file",
    )

    convert.add_argument(
        "--outfile",
        required=True,
        type=Path,
        help="Output TSV file",
    )

    args = parser.parse_args()

    # -------- run detect --------
    if args.command == "detect":
        run_detect(
            case_file=args.case,
            control_file=args.control,
            fc_threshold=args.fc_threshold,
            freq_c_cutoff=args.case_freq_cutoff,
            FDR_threshold=args.fdr_threshold,
            freq_b_threshold=args.control_freq_threshold,
            out_dir=args.outdir,
        )

    # -------- run convert --------
    elif args.command == "convert":
        run_convert(
            input_file=args.infile,
            output_file=args.outfile,
        )

    else:
        parser.print_help()
