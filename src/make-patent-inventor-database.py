#!/usr/bin/env python

"""
Make MSA-patent inventor database
The database produced contains
* patent_id       <- patent unique id (key)
* inventor_id     <- inventor unique id
* inventor_share  <- 1/(# inventors of the patent)

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
        dtype=str)

    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)

    df_patent[[
        'patent_id', 
        'inventor_id', 
        'inventor_share']] \
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
