#!/usr/bin/env python

"""
Make MSA-patent information database
The database produced contains
* patent_id   <- patent unique id (key)
* grant_date  <- grant date -- YYYY-MM-DD
* appln_date  <- application date -- YYYY-MM-DD
* num_claims  <- number of claims

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

    df_patent = pd.read_table(args.input)
    
    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)

    df_patent[[
        'patent_id', 
        'grant_date', 
        'appln_date', 
        'num_claims']] \
    .drop_duplicates() \
    .to_csv(
        args.output, 
        sep='\t', 
        index=False, 
        compression={
            'method':'zip',
            'archive_name':file.replace('.zip','')})


if __name__ == '__main__':
    main()
