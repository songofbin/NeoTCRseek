import pandas as pd
import argparse

def detect_enriched_TCR(unsorted_file, positive_file, negative_file, fold1, fold2, fold3, freq_cutoff, printed, output_file):
    # Read data
    unsorted = pd.read_csv(unsorted_file, sep='\t')
    positive = pd.read_csv(positive_file, sep='\t')
    negative = pd.read_csv(negative_file, sep='\t')

    # Call sort_enrich function
    enriched_df = sort_enrich(unsorted, positive, negative, fold1, fold2, fold3, freq_cutoff, printed)

    # Save result if output file is specified
    if output_file:
        enriched_df.to_csv(output_file, sep='\t', index=False)

    # Save the 'Keep' True cdr3aa to a separate file
    keep_cdr3aa = enriched_df[enriched_df['Keep'] == True]['cdr3aa']
    if output_file:
        cdr3aa_file = output_file.replace('.tsv', '.cdr3aa.list')
        keep_cdr3aa.to_csv(cdr3aa_file, index=False, header=True)
    
    return enriched_df

def sort_enrich(unsorted, positive, negative, fold1=1, fold2=1, fold3=0, freq_cutoff=1e-4, printed=False):
    unsorted = unsorted.add_suffix('_u').rename(columns={'cdr3aa_u': 'cdr3aa'})
    df_m1 = pd.merge(negative, positive, on='cdr3aa', how='outer', suffixes=('_n', '_p'))
    df_m2 = pd.merge(unsorted, df_m1, on='cdr3aa', how='outer')
    df_m2 = df_m2.loc[df_m2['freq_p'] >= 1e-5]
    df_m2 = df_m2.loc[df_m2['freq_u'] >= freq_cutoff]

    # Handle missing frequency values
    df_m2['freq_n'] = df_m2['freq_n'].fillna(1e-6)
    df_m2['freq_n_raw'] = df_m2['freq_n']

    # Fill missing count columns with maximum values
    if 'countSum_u' in df_m2.columns:
        df_m2['countSum_u'] = df_m2['countSum_u'].fillna(df_m2['countSum_u'].max())
        df_m2['countSum_n'] = df_m2['countSum_n'].fillna(df_m2['countSum_n'].max())
        df_m2['countSum_p'] = df_m2['countSum_p'].fillna(df_m2['countSum_p'].max())

    df_m2 = df_m2.fillna(0)
    
    # Calculate ratios
    df_m2['rate_pu'] = df_m2['freq_p'] / df_m2['freq_u']
    df_m2['rate_pn'] = df_m2['freq_p'] / df_m2['freq_n']
    df_m2['rate_un'] = df_m2['freq_u'] / df_m2['freq_n']
    df_m2 = df_m2.round({'rate_pu': 2, 'rate_pn': 2, 'rate_un': 2})

    # Filter enriched clones
    df_keep = df_m2.loc[(df_m2['rate_pu'] > fold1) & 
                        (df_m2['rate_pn'] > fold2) & 
                        (df_m2['rate_un'] > fold3) & 
                        (df_m2['freq_u'] >= freq_cutoff)]

    df_m2['Keep'] = df_m2['cdr3aa'].apply(lambda x: x in set(df_keep['cdr3aa']))
    df_m2.sort_values(by=['freq_p'], ascending=False, inplace=True)
    df_m2.reset_index(drop=True, inplace=True)

    # Summary statistics
    num_unsorted = unsorted.shape[0]
    num_positive = positive.shape[0]
    num_negative = negative.shape[0]
    num_enrich = df_keep.shape[0]

    fre_unsorted = round(df_keep['freq_u'].sum(), 4)
    fre_positive = round(df_keep['freq_p'].sum(), 4)
    fre_negative = round(df_keep['freq_n_raw'].sum(), 4)

    filter_info = '_'.join(map(str, [fold1, fold2, fold3, freq_cutoff]))

    if printed:
        print("\t".join(['filter_info', 'num_unsorted', 'num_positive', 'num_negative', 'num_enrich', 'fre_unsorted', 'fre_positive', 'fre_negative']))
        print("\t".join(map(str, [filter_info, num_unsorted, num_positive, num_negative, num_enrich, fre_unsorted, fre_positive, fre_negative])))
    
    return df_m2

def main():
    parser = argparse.ArgumentParser(description="Detect enriched TCR clones in sorted samples.")
    
    # Add arguments
    parser.add_argument('--unsorted_file', required=True, help="Path to the unsorted sample file (CSV format)")
    parser.add_argument('--positive_file', required=True, help="Path to the positive sample file (CSV format)")
    parser.add_argument('--negative_file', required=True, help="Path to the negative sample file (CSV format)")
    parser.add_argument('--fold1', type=float, default=1, help="Frequency fold threshold between positive and unsorted (default: 1)")
    parser.add_argument('--fold2', type=float, default=1, help="Frequency fold threshold between positive and negative (default: 1)")
    parser.add_argument('--fold3', type=float, default=0, help="Frequency fold threshold between unsorted and negative (default: 0)")
    parser.add_argument('--freq_cutoff', type=float, default=1e-4, help="Frequency cutoff for unsorted clones (default: 1e-4)")
    parser.add_argument('--printed', type=bool, default=False, help="Whether to print summary statistics (default: False)")
    parser.add_argument('--output_file', required=True, help="Path to save the enriched TCR results (CSV format)")

    args = parser.parse_args()

    detect_enriched_TCR(
        unsorted_file=args.unsorted_file,
        positive_file=args.positive_file,
        negative_file=args.negative_file,
        fold1=args.fold1,
        fold2=args.fold2,
        fold3=args.fold3,
        freq_cutoff=args.freq_cutoff,
        printed=args.printed,
        output_file=args.output_file
    )

if __name__ == "__main__":
    main()
