#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import numpy as np
import pandas as pd

def result_reformat(infile, outfile):

    dfs = []

    with open(infile, "r") as f:
        results = f.read().splitlines()

    c = 1
    for line in results:
        columns = line.split()

        motif = columns[3]
        cluster = columns[4:]

        if len(cluster) >= 2:
            nodes = pd.DataFrame({
                "cdr3aa": cluster,
                "cluster": c,
                "motif": motif
            })
            dfs.append(nodes)
            c += 1

    if dfs:
        clusters = pd.concat(dfs, ignore_index=True)
    else:
        clusters = pd.DataFrame(columns=["cdr3aa", "cluster", "motif"])

    clusters.to_csv(outfile, sep="\t", index=False)

if __name__=='__main__':

    if len(sys.argv) != 3:
        print("Usage: python %s <in_file> <out_file>" % sys.argv[0])
        sys.exit(1)

    args = sys.argv
    infile=sys.argv[1]
    outfile=sys.argv[2]

    result_reformat(infile,outfile) 
