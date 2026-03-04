#!/usr/bin/env python3

import sys
import pandas as pd
from pathlib import Path

# Check command-line arguments
if len(sys.argv) != 5:
    print(f"Usage: python {sys.argv[0]} <expanded_TCRs.anno.txt> <GIANA_cluster.txt> <prop_cutoff> <rate_cutoff>")
    sys.exit(1)

infile1 = sys.argv[1]
infile2 = sys.argv[2]
prop_cutoff = float(sys.argv[3])
rate_cutoff = float(sys.argv[4])

outfile = Path(infile2).with_suffix("").as_posix() + "_score.tsv"


def select_detect_and_cluster_TCRs(infile1, infile2, outfile, prop_cutoff, rate_cutoff):
    # Step 1: Load data
    df1 = pd.read_csv(infile1, sep='\t')
    df2 = pd.read_csv(infile2, sep='\t', header=None, comment='#')
    df2 = df2.rename(columns={0: 'cdr3aa', 1: 'cluster'})[['cdr3aa', 'cluster']]

    # Step 2: Cluster matching
    df = pd.merge(df1, df2, on='cdr3aa', how='left')
    df['Detected'] = df['Expanded'] == True
    df_Detected = df[(df.Detected == True) & (df.cluster.notna())]

    cluster_list = df_Detected.cluster.unique().tolist()
    df_keep = df[df['cluster'].isin(cluster_list)]

    # Step 3: Cluster purity calculation
    df_cluster_purity = df_keep.groupby('cluster')['Detected'].mean().reset_index(name='cluster_purity')
    df_keep1 = pd.merge(df_keep, df_cluster_purity, on='cluster', how='left')

    # Step 4: V gene filtering
    df_detect = df_keep1[df_keep1.Detected == True]
    v_count = df_detect.groupby('cluster')['v'].agg(lambda x: len(set(x))).to_frame(name='unique_count')
    filtered_clusters = v_count[v_count.unique_count == 1].index
    df_detect2 = df_detect[df_detect['cluster'].isin(filtered_clusters)]
    df_keep2 = df_keep1[df_keep1['cluster'].isin(filtered_clusters)]

    df_v = df_detect2.groupby('cluster')['v'].agg(lambda x: ', '.join(map(str, set(x)))).reset_index(name='v_true')
    df_keep3 = pd.merge(df_keep2, df_v, on='cluster', how='left')
    df_keep3['v_check'] = df_keep3['v'] == df_keep3['v_true']

    # Step 5: Apply filters
    df_result = df_keep3.sort_values(by=['cluster', 'freq_c'], ascending=[True, False])
    df_result['Detected_filter'] = (df_result.Detected == False) & (df_result.cluster_purity >= prop_cutoff) & (df_result.v_check == True) & (df_result.FC >= rate_cutoff)

    # Step 6: Save results
    df_result['Detected_check'] = (df_result['Detected'] == False) & (df_result['TrueTCR'] == True)
    df_result.to_csv(outfile + ".gz", sep="\t", index=False, compression="gzip")

    # Step 7: Statistics
    df_filter = df_result[df_result.Detected_filter == True][['cdr3aa', 'Detected_check']]
    df_unique = df_filter.drop_duplicates()
    df_unique.to_csv(outfile + ".unique.txt", sep="\t", index=None)

    value_counts_num = df_unique['Detected_check'].value_counts()
    true_num = value_counts_num.get(True, 0)
    false_num = value_counts_num.get(False, 0)
    print(f"{true_num}\t{false_num}", end="\t")


# Run the function
select_detect_and_cluster_TCRs(infile1, infile2, outfile, prop_cutoff, rate_cutoff)
print()
