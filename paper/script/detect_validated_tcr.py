import pandas as pd
import argparse
import sys

def process_files(input_files):
    all_data = []

    for file in input_files:
        df = pd.read_csv(file, sep='\t', usecols=['cdr3aa', 'freq_u', 'Keep'])

        # Convert 'Keep' to boolean and filter rows where Keep is True
        df['Keep'] = df['Keep'].astype(str).str.lower() == 'true'
        df = df[df['Keep']]

        # Add a 'Valid_flag' column to mark valid entries
        df['Valid_flag'] = 1

        # Append necessary columns to the list
        all_data.append(df[['cdr3aa', 'freq_u', 'Valid_flag']])

    # Merge all data and aggregate based on cdr3aa
    merged = pd.concat(all_data, ignore_index=True)
    result = merged.groupby('cdr3aa', as_index=False).agg(
        freq_u=('freq_u', 'max'),
        Valid_number=('Valid_flag', 'sum')
    )

    # Filter based on freq_u and Valid_number thresholds
    result = result[(result['freq_u'] >= 1e-4) | (result['Valid_number'] >= 2)]

    return result

def main():
    parser = argparse.ArgumentParser(description="Count occurrences of cdr3aa with 'Keep' set to True across multiple files")

    # Input and output file arguments
    parser.add_argument('-i', '--input', nargs='+', required=True, help="List of input files")
    parser.add_argument('-o', '--output', required=True, help="Path to output the result")

    args = parser.parse_args()

    # Ensure output file is not one of the input files
    if args.output in args.input:
        sys.exit("Error: output file cannot be one of the input files.")

    result_df = process_files(args.input)

    # Save the result to output file
    result_df.to_csv(args.output, sep='\t', index=False)

if __name__ == "__main__":
    main()
