#!/usr/bin/env python

"""
Make MSA-patent database
The database produced contains
* patent_id   <- patent unique id (key)
* cbsa_id     <- CBSA FIPS code
* cbsa_share  <- fraction of inventors of the patent resident in the CBSA

Author: Carlo Bottai
Copyright (c) 2021 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-02-06

"""


import pandas as pd
import os
from parse_args import parse_io


def main():
    args = parse_io()

    df_patent = pd.read_table(
        args.input,
        usecols=[
            'patent_id', 
            'inventor_id', 
            'inventor_share',
            'cbsa_id']) \
        .drop_duplicates()

    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)

    df_patent \
        .drop(columns='inventor_id') \
        .groupby(['patent_id','cbsa_id'], as_index=False) \
        .agg({
            'inventor_share':'sum'}) \
        .rename(columns={'inventor_share':'cbsa_share'}) \
        .to_csv(
            args.output, 
            sep='\t', 
            index=False, 
            compression={
                'method':'zip',
                'archive_name':file.replace('.zip','')})


if __name__ == '__main__':
    main()
