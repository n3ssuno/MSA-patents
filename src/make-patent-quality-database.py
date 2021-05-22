#!/usr/bin/env python

"""
Make MSA-patent quality database
The database produced contains
* patent_id                <- patent unique id (key)
* num_claims               <- number of claims
* num_citations_5y         <- number of citations received 
                              in the 5 years following the grant year
* num_citations_10y        <- number of citations received 
                              in the 10 years following the grant year
* avg_num_claims_gy        <- average number of claims of a patent 
                              granted in the same year of the focal patent 
                              and belonging to its same USPC class
* avg_num_claims_ay        <- average number of claims of a patent
                              applied in the same year of the focal patent 
                              and belonging to its same USPC class
* avg_num_citations_5y_gy  <- average number of citations received 
                              in the 5 years following the grant year by a patent 
                              granted in the same year of the focal patent 
                              and belonging to its same USPC class
* avg_num_citations_10y_gy <- average number of citations received 
                              in the 10 years following the grant year by a patent 
                              granted in the same year of the focal patent 
                              and belonging to its same USPC class
* avg_num_citations_5y_ay  <- average number of citations received 
                              in the 5 years following the grant year by a patent 
                              applied in the same year of the focal patent 
                              and belonging to its same USPC class
* avg_num_citations_10y_ay <- average number of citations received 
                              in the 10 years following the grant year by a patent 
                              applied in the same year of the focal patent 
                              and belonging to its same USPC class

Author: Carlo Bottai
Copyright (c) 2021 - Carlo Bottai
License: See the LICENSE file.
Date: 2021-02-06

"""


import numpy as np
import pandas as pd
import os
from parse_args import parse_io


def convert_patent_id(patent_id):
    patent_id = pd.to_numeric(
        patent_id, 
        errors='coerce', 
        downcast='unsigned')
    if pd.isna(patent_id):
        patent_id = 0
    return patent_id


def main():
    args = parse_io()

    df_msa_patent_dates = pd.read_table(
        args.input_list[0], # msa_patent_dates.tsv.zip
        dtype={
            'patent_id':np.uint32,
            'grant_date':str,
            'appln_date':str},
        parse_dates=[
            'grant_date',
            'appln_date'])
    
    df_msa_patent_uspc = pd.read_table(
        args.input_list[1], # msa_patent_uspc.tsv.zip
        dtype={
            'patent_id':np.uint32,
            'uspc_class':'category'})
    
    df_msa_patent= pd.merge(
        df_msa_patent_dates, df_msa_patent_uspc, 
        how='outer')
    del df_msa_patent_dates, df_msa_patent_uspc

    df_msa_patent['grant_year'] = df_msa_patent.grant_date.dt.year
    df_msa_patent['appln_year'] = df_msa_patent.appln_date.dt.year

    df_patent = pd.read_table(
        args.input_list[2], # patent_info.tsv.zip
        usecols=[
            'patent_id',
            'grant_date',
            'appln_date',
            'uspc_class',
            'num_claims'],
        dtype={
            'patent_id':np.uint32,
            'grant_date':str,
            'appln_date':str,
            'uspc_class':'category',
            'num_claims':float}) \
        .drop_duplicates()

    df_patent['grant_date'] = pd.to_datetime(
        df_patent.grant_date, errors='coerce')
    df_patent['appln_date'] = pd.to_datetime(
        df_patent.appln_date, errors='coerce')

    df_patent = df_patent[
        (~df_patent.grant_date.isna()) & 
        (~df_patent.appln_date.isna())]

    df_patent['grant_year'] = df_patent.grant_date.dt.year
    df_patent['appln_year'] = df_patent.appln_date.dt.year

    grant_date_last = df_patent.grant_date.max()

    df_avg_num_claims_gy = df_patent \
        .groupby([
            'grant_year',
            'uspc_class']) \
        .agg({
            'num_claims':'mean'}) \
        .rename(columns={
            'num_claims':'avg_num_claims_gy'})

    df_msa_patent = pd.merge(
        df_msa_patent, df_avg_num_claims_gy,
        left_on=['grant_year', 'uspc_class'], right_index=True,
        how='left')

    df_avg_num_claims_ay = df_patent \
        .groupby([
            'appln_year',
            'uspc_class']) \
        .agg({
            'num_claims':'mean'}) \
        .rename(columns={
            'num_claims':'avg_num_claims_ay'})

    df_msa_patent = pd.merge(
        df_msa_patent, df_avg_num_claims_ay,
        left_on=['appln_year', 'uspc_class'], right_index=True,
        how='left')

    subset = df_msa_patent.uspc_class.isna()

    df_avg_num_claims_gy = df_patent \
        .groupby([
            'grant_year']) \
        .agg({
            'num_claims':'mean'}) \
        .rename(columns={
            'num_claims':'avg_num_claims_gy'})

    df_msa_patent = pd.concat([
        df_msa_patent[~subset],
        pd.merge(
            df_msa_patent[subset] \
                .drop(columns='avg_num_claims_gy'), 
            df_avg_num_claims_gy,
            left_on=['grant_year'], right_index=True,
            how='left')], 
        sort=True)

    subset = df_msa_patent.uspc_class.isna()

    df_avg_num_claims_ay = df_patent \
        .groupby([
            'appln_year']) \
        .agg({
            'num_claims':'mean'}) \
        .rename(columns={
            'num_claims':'avg_num_claims_ay'})

    df_msa_patent = pd.concat([
        df_msa_patent[~subset],
        pd.merge(
            df_msa_patent[subset] \
                .drop(columns='avg_num_claims_ay'), 
            df_avg_num_claims_ay,
            left_on=['appln_year'], right_index=True,
            how='left')], 
        sort=True)

    del df_avg_num_claims_gy, df_avg_num_claims_ay, subset

    df_patent.drop(columns='num_claims', inplace=True)

    ##########################

    df_msa_citation = pd.merge(
        df_msa_citation, df_patent)
    df_msa_citation = pd.merge(
        df_msa_citation, df_patent \
            [['patent_id','grant_date']] \
            .rename(columns={
                'patent_id':'forward_citation_id',
                'grant_date':'forward_citation_grant_date'}))
    # del df_patent

    df_msa_citation['time_length'] = df_msa_citation \
        .forward_citation_grant_date \
        .sub(df_msa_citation.grant_date)

    df_msa_citation = df_msa_citation[df_msa_citation.time_length.dt.days<=10*365]

    df_msa_citation_10y = df_msa_citation \
        .groupby('patent_id') \
        .agg({'forward_citation_id':'nunique'}) \
        .rename(columns={'forward_citation_id':'num_citations_10y'})

    df_msa_citation = df_msa_citation[df_msa_citation.time_length.dt.days<=5*365]

    df_msa_citation_5y = df_msa_citation \
        .groupby('patent_id') \
        .agg({'forward_citation_id':'nunique'}) \
        .rename(columns={'forward_citation_id':'num_citations_5y'})

    df_msa_citation = pd.merge(
        df_msa_citation_5y, df_msa_citation_10y,
        left_index=True, right_index=True,
        how='outer')
    del df_msa_citation_5y, df_msa_citation_10y

    df_msa_patent = pd.merge(
        df_msa_patent, df_msa_citation,
        left_on='patent_id', right_index=True,
        how='left')
    del df_msa_citation

    for years in [5,10]:
        col = f'num_citations_{years}y'
        threshold = grant_date_last - pd.tseries.offsets.Day(years*365)
        df_msa_patent[col] = df_msa_patent[col] \
            .fillna(0)
        df_msa_patent.loc[
            df_msa_patent.grant_date > threshold,
            col] = np.nan

    ##########################

    # CITATIONS

    df_avg_num_citations_gy = df_patent_citation \
        .groupby([
            'grant_year',
            'uspc_class']) \
        .agg({
            'num_citations_5y':'mean',
            'num_citations_10y':'mean'}) \
        .rename(columns={
            'num_citations_5y':'avg_num_citations_5y_gy',
            'num_citations_10y':'avg_num_citations_10y_gy'})

    df_msa_patent = pd.merge(
        df_msa_patent, df_avg_num_citations_gy,
        left_on=['grant_year', 'uspc_class'], right_index=True,
        how='left')

    df_avg_num_citations_ay = df_patent_citation \
        .groupby([
            'appln_year',
            'uspc_class']) \
        .agg({
            'num_citations_5y':'mean',
            'num_citations_10y':'mean'}) \
        .rename(columns={
            'num_citations_5y':'avg_num_citations_5y_ay',
            'num_citations_10y':'avg_num_citations_10y_ay'})

    df_msa_patent = pd.merge(
        df_msa_patent, df_avg_num_citations_ay,
        left_on=['appln_year', 'uspc_class'], right_index=True,
        how='left')

    subset = df_msa_patent.uspc_class.isna()

    df_avg_num_citations_gy = df_patent_citation \
        .groupby([
            'grant_year']) \
        .agg({
            'num_citations_5y':'mean',
            'num_citations_10y':'mean'}) \
        .rename(columns={
            'num_citations_5y':'avg_num_citations_5y_gy',
            'num_citations_10y':'avg_num_citations_10y_gy'})

    df_msa_patent = pd.concat([
        df_msa_patent[~subset],
        pd.merge(
            df_msa_patent[subset] \
                .drop(columns=[
                    'avg_num_citations_5y_gy',
                    'avg_num_citations_10y_gy']), 
            df_avg_num_citations_gy,
            left_on=['grant_year'], right_index=True,
            how='left')], 
        sort=True)

    df_avg_num_citations_ay = df_patent_citation \
        .groupby([
            'appln_year']) \
        .agg({
            'num_citations_5y':'mean',
            'num_citations_10y':'mean'}) \
        .rename(columns={
            'num_citations_5y':'avg_num_citations_5y_ay',
            'num_citations_10y':'avg_num_citations_10y_ay'})

    df_msa_patent = pd.concat([
        df_msa_patent[~subset],
        pd.merge(
            df_msa_patent[subset] \
                .drop(columns=[
                    'avg_num_citations_5y_ay',
                    'avg_num_citations_10y_ay']), 
            df_avg_num_citations_ay,
            left_on=['appln_year'], right_index=True,
            how='left')], 
        sort=True)

    ##########################

    df_msa_patent = df_msa_patent[[
            'patent_id', 
            'num_claims',
            'num_citations_5y',
            'num_citations_10y',
            'avg_num_claims_gy',
            'avg_num_claims_ay',
            'avg_num_citations_5y_gy',
            'avg_num_citations_10y_gy',
            'avg_num_citations_5y_ay',
            'avg_num_citations_10y_ay']] \
        .drop_duplicates()

    ##########################

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
