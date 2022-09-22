#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
# oe_bls_cex_pumd
## Overview
---
This process
- downloads the MSA summary spreadsheets for a set of years
- opens and combines them into pandas dataframe then
- maps the rows to CEX variables

The MSA level data are not geographically inclusive of the US population,
and the BLS has only selected the larges 2 dozen MSAs,
so this data may be only useful as providing a control to the model results.
"""

import pandas as pd
import wget
import zipfile
import os
from functools import reduce
import warnings
warnings.simplefilter("ignore")


def oe_bls_cex_msa_download(years, regions, msadir, cexurl):
    
    # Avoid conflicts with any previously downloaded
        
    try:
        os.mkdir(msadir)
    except OSError as err:
        print()
        print("Destination directory '"+msadir+"already exists.")
        print("Please remove it or select a new destination directory.")
        print()
        raise err

    for year in years:
        for region in regions:
            wget.download(cexurl+'tables/geographic/mean/'+
                          'cu-msa-'+region+'-2-year-average-'+year+'.xlsx',
                      out=msadir,
#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
# oe_bls_cex_pumd
## Overview
---
This process
- downloads the MSA summary spreadsheets for a set of years
- opens and combines them into pandas dataframe then
- maps the rows to CEX variables

The MSA level data are not geographically inclusive of the US population,
and the BLS has only selected the larges 2 dozen MSAs,
so this data may be only useful as providing a control to the model results.
"""

import pandas as pd
import wget
import zipfile
import os
from functools import reduce
import warnings
warnings.simplefilter("ignore")


def oe_bls_cex_msa_download(years, regions, msadir, cexurl):
    
    # Avoid conflicts with any previously downloaded
        
    try:
        os.mkdir(msadir)
    except OSError as err:
        print()
        print("Destination directory '"+msadir+"already exists.")
        print("Please remove it or select a new destination directory.")
        print()
        raise err

    for year in years:
        for region in regions:
            wget.download(cexurl+'tables/geographic/mean/'+
                          'cu-msa-'+region+'-2-year-average-'+year+'.xlsx',
                      out=msadir,
                      bar=None)
    #For example:
    #    wget https://www.bls.gov/cex/tables/geographic/mean/cu-msa-midwest-2-year-average-2020.xlsx
    
    return None
    
def oe_bls_cex_msa_open(year, regions, msadir):
    """
    For a given year and set of Census regions, this function
        opens the MSA summary spreadsheets
        combines the regions into one dataframe
        adds the CEX variable name related to each summary Item.
        and the BLS CPI Code replacing the MSA names as colums
        
    to return a dataframe with the MSAs as the major columns
    
    :param year:      a string as the selected year, '2018', e.g.
    :param regions:   a list of the requested regions, ['midwest','northeast','west','south'] eg
    :param msadir:    a string for the OS path where source MSA xls are stored
    
    :return msa:      a dataframe with Items ("Income",Food","Shelter", eg) as rows
                        and MSAs as columns ("Detroit","Chicago","Philadelphia") eg

    Notes
    -----
    The MSA summary reports have 45 categories of spending (some Title rows, one calculation)
    and 27 columns - 4 regional totals with 23 largest MSAs. 

    We need to add the CEX Variable name associated with each report row.
    and replace the reports MSA column names with related CPI codes.
        
    * The CEX uses the MSA as its Primary Sampling Unit (PSU) so the CEX's PSU column has MSA
    codes in it. Unfortunately the BLS maintains its own version of MSA codes called CPI
    Codes.

    The two reference sheets are manually curated from:
    
        National Bureau of Economic Research (NBER)  https://www.nber.org/
          "CPI MSA to Unemployment (OMB) MSA.xlsx"

        CEX Hierarchical Groupings
        
    """

    # The reference sheets are found in the dir above the msadir
    refdir = msadir[:msadir[:-2].rfind("\\")+1]
    cexvariables = pd.read_excel(refdir + 'CEXVariables.xlsx')    
    msacodes = pd.read_excel(refdir + 'MSACodes.xlsx')
    
    filelist = []
    for region in regions:
        df = pd.read_excel(msadir+"cu-msa-"+region+"-2-year-average-"+year+".xlsx", skiprows=2)
        df = df[df.iloc[:, 1].notnull()]
        df.columns = [c.replace('\n',' ').replace('- ','-') for c in df.columns]
        for c in df.columns:
            if c == "Item":
                df[c] = df[c].replace({' a/ ': '', ':': ''}, regex=True)
            else:
                df[c] = df[c].replace({'\$': '', ',': '','b/ ':''}, regex=True).astype(float)
        filelist.append(df)

    msa = reduce(lambda left,right: 
                        pd.merge(left,right,on=['Item'], how='outer'), 
                        filelist)

    # Replace the city names with CPI codes
    msa.drop([c for c in msa.columns if "All consumer units in" in c],
             axis=1,
             inplace=True)
    
    msadict = {}
    for i,m in msacodes.iterrows():
        msadict[m.Short] = m.Area
    for i in range(msa.shape[1]):
        if i == 0:
            colcodes = ['Item']
        else:
            colcodes.append(msadict[msa.columns[i]])
    msa.columns = colcodes
    
    msacoded = pd.merge(msa,cexvariables,left_on="Item",right_on="ReportTitle",how="inner")

    return msacoded

if __name__ == "__main__":
    
    CEXURL = 'https://www.bls.gov/cex/'
    MSADIR = "D:\\Open Environments\\data\\bls\\cex\\msa\\"

    REGIONS = ['midwest','northeast','west','south']
    YEARS = ['2016','2017','2018','2019','2020']
    #YEARS = ["2018"] # ['2016','2017','2018','2019','2020']
    
    #oe_bls_cex_msa_download(years=YEARS, regions=REGIONS, msadir=MSADIR, cexurl=CEXURL)
    
    for year in YEARS:
        df = oe_bls_cex_msa_open(year, regions=REGIONS, msadir=MSADIR)
    
    print("Done")

