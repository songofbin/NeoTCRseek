from pathlib import Path
import logging
import pandas as pd

from .pipeline import convert_VDJtools

def run_convert(input_file: Path, output_file: Path):
    """
    Convert a TCR TSV file to standard NeoTCRseek format.
    """
    logging.info(f"Converting {input_file} -> {output_file} ...")

    if not input_file.exists():
        logging.error(f"Input file not found: {input_file}")
        raise FileNotFoundError(f"{input_file} does not exist")

    df = convert_VDJtools(input_file)
    df.to_csv(output_file, sep="\t", index=False)

    logging.info("Conversion finished successfully.")

