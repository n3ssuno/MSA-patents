#!/usr/bin/env python

"""
Make MSA-patent grant/application date database
The database produced contains
* patent_id                <- patent unique id (key)
* grant_date               <- grant date -- YYYY-MM-DD
* appln_date               <- application date -- YYYY-MM-DD

Author: Carlo Bottai
Copyright (c) 2021 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-03-05

"""


import numpy as np
import pandas as pd
import os
from parse_args import parse_io


def main():
    args = parse_io()

    df_msa_patent = pd.read_table(
        args.input_list[0], # msa_patent.tsv.zip
        usecols=['patent_id'],
        dtype=np.uint32)
    
    df_msa_citation = pd.read_table(
        args.input_list[1], # msa_citation.tsv.zip
        dtype=np.uint32)

    patent_ids = set(df_msa_patent.patent_id) \
        .union(df_msa_citation.forward_citation_id)
    
    del df_msa_patent

    df_msa_patent = pd.read_table(
        args.input_list[2], # patent_info.tsv.zip
        usecols=[
            'patent_id',
            'grant_date',
            'appln_date'],
        dtype={
            'patent_id':np.uint32,
            'grant_date':str,
            'appln_date':str}) \
        .drop_duplicates() \
        .query('patent_id in @patent_ids')

    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)

    df_msa_patent.to_csv(
        args.output, 
        sep='\t', 
        index=False, 
        compression={
            'method':'zip',
            'archive_name':file.replace('.zip','')})


if __name__ == '__main__':
    main()
