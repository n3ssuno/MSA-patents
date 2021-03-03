#!/usr/bin/env python

"""
Make MSA-patent information database
The database produced contains
* patent_id                <- patent unique id (key)
* grant_date               <- grant date -- YYYY-MM-DD
* appln_date               <- application date -- YYYY-MM-DD
* uspc_class               <- USPC main class
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

uspc_classes = [
    '002','004','005','007','008','012','014','015','016','019','023',
    '024','026','027','028','029','030','033','034','036','037','038',
    '040','042','043','044','047','048','049','051','052','053','054',
    '055','056','057','059','060','062','063','065','066','068','069',
    '070','071','072','073','074','075','076','079','081','082','083',
    '084','086','087','089','091','092','095','096','099','100','101',
    '102','104','105','106','108','109','110','111','112','114','116',
    '117','118','119','122','123','124','125','126','127','128','131',
    '132','134','135','136','137','138','139','140','141','142','144',
    '147','148','149','150','152','156','157','159','160','162','163',
    '164','165','166','168','169','171','172','173','174','175','177',
    '178','180','181','182','184','185','186','187','188','190','191',
    '192','193','194','196','198','199','200','201','202','203','204',
    '205','206','208','209','210','211','212','213','215','216','217',
    '218','219','220','221','222','223','224','225','226','227','228',
    '229','231','232','234','235','236','237','238','239','241','242',
    '244','245','246','248','249','250','251','252','254','256','257',
    '258','260','261','264','266','267','269','270','271','273','276',
    '277','278','279','280','281','283','285','289','290','291','292',
    '293','294','295','296','297','298','299','300','301','303','305',
    '307','310','312','313','314','315','318','320','322','323','324',
    '326','327','329','330','331','332','333','334','335','336','337',
    '338','340','341','342','343','345','346','347','348','349','351',
    '352','353','355','356','358','359','360','361','362','363','365',
    '366','367','368','369','370','372','373','374','375','376','377',
    '378','379','380','381','382','383','384','385','386','388','392',
    '396','398','399','400','401','402','403','404','405','406','407',
    '408','409','410','411','412','413','414','415','416','417','418',
    '419','420','422','423','424','425','426','427','428','429','430',
    '431','432','433','434','435','436','438','439','440','441','442',
    '445','446','449','450','451','452','453','454','455','460','462',
    '463','464','470','472','473','474','475','476','477','482','483',
    '492','493','494','501','502','503','504','505','506','507','508',
    '510','512','514','516','518','520','521','522','523','524','525',
    '526','527','528','530','532','534','536','540','544','546','548',
    '549','552','554','556','558','560','562','564','568','570','585',
    '588','600','601','602','604','606','607','623','700','701','702',
    '703','704','705','706','707','708','709','710','711','712','713',
    '714','715','716','717','718','719','720','725','726','800','850',
    '901','902','903','930','968','976','977','984','987','D01','D02',
    'D03','D04','D05','D06','D07','D08','D09','D10','D11','D12','D13',
    'D14','D15','D16','D17','D18','D19','D20','D21','D22','D23','D24',
    'D25','D26','D27','D28','D29','D30','D32','D34','D99','PLT']

def convert_uspc_class(uspc_class):
    if str(uspc_class) in uspc_classes:
        return uspc_class
    return 'XXX'

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
            'date',
            'num_claims'],
        dtype={
            'date':str,
            'num_claims':float},
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

    df_patex = pd.read_csv(
        args.input_list[4], # application_data.csv.zip
        usecols=[
            'uspc_class', 
            'patent_number'],
        converters={
            'uspc_class':convert_uspc_class,
            'patent_number':convert_patent_id}) \
        .rename(columns={
            'patent_number':'patent_id'}) \
        .drop_duplicates() \
        .dropna() \
        .query('patent_id!=0 & uspc_class!="XXX"') \
        .astype({
            'uspc_class':str,
            'patent_id':np.uint32})

    df_patex['uspc_class'] = pd.Categorical(df_patex.uspc_class)

    df_patent = pd.merge(
        df_patent, df_patex, 
        how='left')
    del df_patex
    
    df_msa_patent = df_patent[df_patent.patent_id.isin(patent_ids)].copy()

    for date_column in ['grant_date', 'appln_date']:
        df_msa_patent = fix_dates(df_msa_patent, date_column)
        df_msa_patent[date_column] = pd.to_datetime(
            df_msa_patent[date_column])

    df_patent['grant_date'] = pd.to_datetime(
        df_patent.grant_date, errors='coerce')
    df_patent['appln_date'] = pd.to_datetime(
        df_patent.appln_date, errors='coerce')

    df_patent = df_patent[
        (~df_patent.grant_date.isna()) & 
        (~df_patent.appln_date.isna())]

    df_patent['grant_year'] = df_patent.grant_date.dt.year
    df_patent['appln_year'] = df_patent.appln_date.dt.year

    df_msa_patent['grant_year'] = df_msa_patent.grant_date.dt.year
    df_msa_patent['appln_year'] = df_msa_patent.appln_date.dt.year

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

    df_patent_citation = pd.read_table(
        args.input_list[5], # uspatentcitation.tsv.zip
        usecols=[
            'patent_id',
            'citation_id'], 
        converters={
            'patent_id':convert_patent_id,
            'citation_id':convert_patent_id}) \
        .rename(columns={
            'patent_id':'forward_citation_id',
            'citation_id':'patent_id'}) \
        .query('patent_id!=0 & forward_citation_id!=0') \
        .astype({
            'patent_id':np.uint32,
            'forward_citation_id':np.uint32})

    df_patent_citation = pd.merge(
        df_patent_citation, df_patent)
    df_patent_citation = pd.merge(
        df_patent_citation, df_patent \
            [['patent_id','grant_date']] \
            .rename(columns={
                'patent_id':'forward_citation_id',
                'grant_date':'forward_citation_grant_date'}))
    # del df_patent

    df_patent_citation['time_length'] = df_patent_citation \
        .forward_citation_grant_date \
        .sub(df_patent_citation.grant_date)

    df_patent_citation = df_patent_citation[df_patent_citation.time_length.dt.days<=10*365]

    df_patent_citation_10y = df_patent_citation \
        .groupby('patent_id') \
        .agg({'forward_citation_id':'nunique'}) \
        .rename(columns={'forward_citation_id':'num_citations_10y'})

    df_patent_citation = df_patent_citation[df_patent_citation.time_length.dt.days<=5*365]

    df_patent_citation_5y = df_patent_citation \
        .groupby('patent_id') \
        .agg({'forward_citation_id':'nunique'}) \
       .rename(columns={'forward_citation_id':'num_citations_5y'})

    df_patent_citation = pd.merge(
        df_patent_citation_5y, df_patent_citation_10y,
        left_index=True, right_index=True,
        how='outer')
    del df_patent_citation_5y, df_patent_citation_10y

    df_patent_citation = pd.merge(
        df_patent_citation, df_patent,
        left_index=True, right_on='patent_id')

    for years in [5,10]:
        col = f'num_citations_{years}y'
        threshold = grant_date_last - pd.tseries.offsets.Day(years*365)
        df_patent_citation[col] = df_patent_citation[col] \
            .fillna(0)
        df_patent_citation.loc[
            df_patent_citation.grant_date > threshold,
            col] = np.nan

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
            'grant_date', 
            'appln_date', 
            'uspc_class',
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
