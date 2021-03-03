#!/usr/bin/env python

"""
Make MSA-patent information database
The database produced contains
* patent_id       <- patent unique id (key)
* cpc_class       <- CPC subclass; 4 digits class
* cpc_class_count <- Number of main groups of the CPC subclass that appear in the patent

Author: Carlo Bottai
Copyright (c) 2021 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-03-02

"""


import pandas as pd
import os
from parse_args import parse_io


def main():
    args = parse_io()

    patent_ids = set(
            pd.read_table(
                args.input_list[0], # msa_patent.tsv.zip
                usecols=[
                    'patent_id'],
                dtype=int) \
                .patent_id) \
        .union(
            pd.read_table(
                args.input_list[1], # msa_citation.tsv.zip
                usecols=[
                    'forward_citation_id'],
                dtype=int) \
                .forward_citation_id)

    df_cpc = pd.read_table(
        args.input_list[2], # cpc_current.tsv.zip
        usecols=[
            'patent_id',
            'group_id',
            'subgroup_id'],
        dtype={
            'patent_id':int,
            'group_id':str,
            'subgroup_id':str}) \
        .rename(columns={
            'group_id':'cpc_class'})
    
    df_cpc = df_cpc[df_cpc.patent_id.isin(patent_ids)]
    
    df_cpc['subgroup_id'] = df_cpc \
        .subgroup_id \
        .apply(lambda row: row.split('/')[0])
    df_cpc.drop_duplicates(inplace=True)
    
    df_cpc = df_cpc[
        (df_cpc.subgroup_id.str.len()<8) & \
        (~df_cpc.subgroup_id.str.startswith('Y'))]
        
    df_cpc = df_cpc \
        .value_counts([
            'patent_id',
            'cpc_class']) \
        .reset_index(name='cpc_class_count') \
        .sample(frac=1, random_state=1)
    
    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)

    df_cpc.to_csv(
        args.output, 
        sep='\t', 
        index=False, 
        compression={
            'method':'zip',
            'archive_name':file.replace('.zip','')})


if __name__ == '__main__':
    main()
