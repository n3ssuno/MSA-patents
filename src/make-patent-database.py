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
from parse_args import parse_io


def main():
    args = parse_io()

    df_patent = pd.read_table(
        args.input_list[0], # patent.tsv.zip
        usecols=[
            'id'],
        dtype=str) \
        .rename(columns={
            'id':'patent_id'})
    df_patent = df_patent[df_patent.patent_id.str.isnumeric()]

    df_patent_inventor = pd.read_table(
        args.input_list[1], # patent_inventor.tsv.zip
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
        args.input_list[2], # location.tsv.zip
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
    df_cbsa = gpd.read_file( # cb_2019_us_cbsa_20m.zip
        f'zip://{args.input_list[3]}') \
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
    del df_cbsa

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
