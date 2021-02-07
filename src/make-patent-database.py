#!/usr/bin/env python

"""
Make MSA patents database

Author: Carlo Bottai
Copyright (c) 2021 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-02-05

"""


import pandas as pd
import geopandas as gpd
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

    df_patent = pd.read_table(
        args.input_list[0], # patent.tsv.zip
        usecols=[
            'id',
            'date',
            'num_claims'],
        dtype=str) \
        .rename(columns={
            'id':'patent_id',
            'date':'grant_date'})
    df_patent = df_patent[df_patent.patent_id.str.isnumeric()]

    df_application = pd.read_table(
        args.input_list[1], # application.tsv.zip
        usecols=[
            'patent_id',
            'date'],
        dtype=str) \
        .rename(columns={
            'date':'appln_date'})

    df_patent = pd.merge(df_patent, df_application)
    del df_application

    df_patent_inventor = pd.read_table(
        args.input_list[2], # patent_inventor.tsv.zip
        dtype=str) \
        .dropna()

    df_patent = pd.merge(df_patent, df_patent_inventor)
    del df_patent_inventor

    df_patent = pd.merge(
        df_patent, 
        1 / df_patent \
            .groupby('patent_id') \
            .agg({
                'inventor_id':'nunique'}) \
            .rename(columns={
                'inventor_id':'inventor_share'}),
        left_on='patent_id', right_index=True, 
        how='left')

    df_location = pd.read_table(
        args.input_list[3], # location.tsv.zip
        usecols=[
            'id',
            'latitude',
            'longitude'],
        dtype={
            'id':str,
            'latitude':float,
            'longitude':float}) \
        .rename(columns={
            'id':'location_id'})

    df_patent = pd.merge(df_patent, df_location)
    del df_location

    geometry = gpd.points_from_xy(
        df_patent.longitude, df_patent.latitude)
    df_patent = gpd.GeoDataFrame(
        df_patent, geometry=geometry, crs='EPSG:4269')

    df_patent.drop(
        columns=[
            'location_id',
            'latitude',
            'longitude'], 
        inplace=True)

    # M1 = Metropolitan areas
    df_cbsa = gpd.read_file( # cb_2018_us_cbsa_20m.zip
        f'zip://{args.input_list[4]}') \
        .query('LSAD=="M1"') \
        .drop(columns=['LSAD','ALAND','AWATER']) \
        .rename(columns={
            'CSAFP':'csa_id',
            'CBSAFP':'cbsa_id',
            'NAME':'cbsa_label'})

    df_patent = gpd.sjoin(
        df_patent, df_cbsa, 
        op='within') \
        .drop(columns='index_right')
    df_patent = pd.DataFrame(df_patent)

    for date_column in ['grant_date', 'appln_date']:
        df_patent = fix_dates(df_patent, date_column)

    dir, file = os.path.split(args.output)
    if not os.path.exists(dir):
        os.makedirs(dir)
    df_patent.to_csv(
        args.output, 
        sep='\t', 
        index=False, 
        compression={
            'method':'zip',
            'archive_name':file.replace('.zip','')})


if __name__ == '__main__':
    main()
