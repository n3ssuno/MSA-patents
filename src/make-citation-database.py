#!/usr/bin/env python

"""
Make MSA-patents forward-citations database

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

    msa_patents = pd.read_table(
        args.input_list[0], # msa_patents.tsv.zip
        usecols=[
            'patent_id'],
        dtype=str) \
        .patent_id.unique()

    df_patent_citation = pd.read_table(
        args.input_list[1], # uspatentcitation.tsv.zip
        usecols=[
            'patent_id',
            'citation_id'], 
        dtype=str)
    
    # Build the dataframe, filtering only the citations going to utility patents 
    #  located into a MSA and coming from a utility patent
    # Rename to columns so that the dataframe can be merged with the other
    #  dataframes of the MSA-patents project:
    #   - patent_id is the cited patent
    #   - forward_citation_id is the citing patent
    df_patent_citation = df_patent_citation[
        (df_patent_citation.citation_id.isin(msa_patents)) &
        (df_patent_citation.patent_id.str.isnumeric())] \
        .rename(columns={
            'patent_id':'forward_citation_id',
            'citation_id':'patent_id'})
    
    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    df_patent_citation.to_csv(
        args.output, 
        sep='\t', 
        index=False, 
        compression={
            'method':'zip',
            'archive_name':file.replace('.zip','')})


if __name__ == '__main__':
    main()
