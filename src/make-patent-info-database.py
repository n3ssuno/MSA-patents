#!/usr/bin/env python

"""
Make MSA-patent information database
The database produced contains
* patent_id   <- patent unique id (key)
* grant_date  <- grant date -- YYYY-MM-DD
* appln_date  <- application date -- YYYY-MM-DD
* num_claims  <- number of claims
* uspc_class  <- USPC main class

Author: Carlo Bottai
Copyright (c) 2021 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-02-06

"""


import pandas as pd
import os
import requests
from parse_args import parse_io


def fix_dates(dataframe:pd.DataFrame, dates_column:str):
    """Fix wrong dates in the PatentsView database
    Some (grant and application) dates on PatentsView are wrongly reported 
      and cannot be converted into proper dates. However, if you look on the
      PatentsView website, most (all?) are correct. Therefore, this module
      uses the PatentsView APIs to retrieve the correct dates 
      (or, as a second-best, it tries to fix them with a simple heuristic)
    """
    # Use the PatentsView API to fix those application dates 
    #  that cannot be coerced into proper dates
    dataframe['date_'] = pd.to_datetime(
        dataframe[dates_column], errors='coerce')
    dataframe.sort_values(by=['patent_id','date_'], inplace=True)
    dataframe.set_index('patent_id', inplace=True)
    patents_to_fix = ','.join([f'{{"patent_number":"{patent_id}"}}' \
        for patent_id in dataframe[dataframe.date_.isna()].index])
    patents_to_fix_n = sum(dataframe.date_.isna())
    if patents_to_fix_n>0:
        query = ''.join([
            'https://api.patentsview.org/patents/query?q={"_or":[',
            patents_to_fix,
            ']}&f=["patent_number","patent_date"]&o={"per_page":',
            str(patents_to_fix_n), '}'])
        response = requests.get(query)
        df_fix = pd.DataFrame(response.json()['patents'], dtype=str)
        df_fix.rename(columns={
            'patent_number':'patent_id', 
            'patent_date':dates_column}, inplace=True)
        df_fix.sort_values(by=['patent_id',dates_column], inplace=True)
        df_fix.set_index('patent_id', inplace=True)
        dataframe.update(df_fix)
    dataframe.drop(columns='date_', inplace=True)
    dataframe.reset_index(inplace=True)
    dataframe.sort_values(by=['patent_id',dates_column], inplace=True)
        
    # At this point, all the mistakes should have been fixed
    #  Anyhow, the script will fix dates that are possibly still wrong 
    #  applying some heuristic with the best guesses we can do, 
    #  given the information provided
    # Fix any date that has "00" as day, putting "01" inplace
    subset = dataframe[dates_column].str.endswith('00')
    if len(subset)>0:
        dataframe.loc[
            subset,dates_column] = dataframe.loc[
                subset,dates_column].str[:-2] + '01'
        # Fix any date that who's year doesn't start with "19" or "20", 
        #  putting "19" inplace
        subset = dataframe[dates_column].str[:2].isin(['19','20'])
        dataframe.loc[
            ~subset,dates_column] = '19' + dataframe.loc[
                ~subset,dates_column].str[2:]
    
    return dataframe


def main():
    args = parse_io()

    df_msa_patent = pd.read_table(
        args.input_list[0], # msa_patent.tsv.zip
        usecols=['patent_id'],
        dtype=str)
    
    df_msa_citation = pd.read_table(
        args.input_list[1], # msa_citation.tsv.zip
        usecols=['forward_citation_id'],
        dtype=str)

    patent_ids = set(df_msa_patent.patent_id) \
        .union(df_msa_citation.forward_citation_id)
    
    del df_msa_patent, df_msa_citation

    df_patent = pd.read_table(
        args.input_list[2], # patent.tsv.zip
        usecols=[
            'id',
            'date',
            'num_claims'],
        dtype=str) \
        .rename(columns={
            'id':'patent_id',
            'date':'grant_date'})

    df_patent = df_patent[df_patent.patent_id.isin(patent_ids)]

    df_application = pd.read_table(
        args.input_list[3], # application.tsv.zip
        usecols=[
            'patent_id',
            'date'],
        dtype=str) \
        .rename(columns={
            'date':'appln_date'})

    df_patent = pd.merge(df_patent, df_application)
    del df_application

    for date_column in ['grant_date', 'appln_date']:
        df_patent = fix_dates(df_patent, date_column)
    
    df_patex = pd.read_csv(
        args.input_list[4], # application_data.csv.zip
        usecols=[
            'uspc_class', 
            'patent_number'],
        dtype=str) \
        .rename(columns={
            'patent_number': 'patent_id'}) \
        .dropna()
    
    df_patent = pd.merge(
        df_patent, df_patex, 
        how='left')
    del df_patex

    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)

    df_patent[[
        'patent_id', 
        'grant_date', 
        'appln_date', 
        'num_claims',
        'uspc_class']] \
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
