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
import requests
from parse_args import parse_io


def convert_patent_id(patent_id):
    patent_id = pd.to_numeric(
        patent_id, 
        errors='coerce', 
        downcast='unsigned')
    if pd.isna(patent_id):
        patent_id = 0
    return patent_id

def convert_grant_year(grant_date):
    grant_date = pd.to_datetime(grant_date, errors='coerce')
    if pd.isna(grant_date):
        grant_date = 0
    else:
        grant_year = grant_date.year
    grant_year = pd.to_numeric(grant_year, downcast='unsigned')
    return grant_year

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
        dtype=np.uint32)
    
    df_msa_citation = pd.read_table(
        args.input_list[1], # msa_citation.tsv.zip
        dtype=np.uint32)

    patent_ids = set(df_msa_patent.patent_id) \
        .union(df_msa_citation.forward_citation_id)
    
    del df_msa_patent

    df_patent = pd.read_table(
        args.input_list[2], # patent.tsv.zip
        usecols=[
            'id',
            'date'],
        dtype={
            'date':str},
        converters={
            'id':convert_patent_id}) \
        .rename(columns={
            'id':'patent_id',
            'date':'grant_date'}) \
        .drop_duplicates() \
        .query('patent_id!=0') \
        .astype({
            'patent_id':np.uint32})

    df_application = pd.read_table(
        args.input_list[3], # application.tsv.zip
        usecols=[
            'patent_id',
            'date'],
        dtype={
            'date':str},
        converters={
            'patent_id':convert_patent_id}) \
        .rename(columns={
            'date':'appln_date'}) \
        .drop_duplicates() \
        .query('patent_id!=0') \
        .astype({
            'patent_id':np.uint32})

    df_patent = pd.merge(
        df_patent, df_application, 
        how='left')
    del df_application

    df_msa_patent = df_patent[df_patent.patent_id.isin(patent_ids)].copy()

    for date_column in ['grant_date', 'appln_date']:
        df_msa_patent = fix_dates(df_msa_patent, date_column)
        df_msa_patent[date_column] = pd.to_datetime(
            df_msa_patent[date_column])

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
