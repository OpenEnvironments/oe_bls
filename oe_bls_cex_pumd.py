#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
# oe_bls_cex_pumd
## Overview
---

The Consumer Expenditure Survey represents national estimates based upon two original
data collections: a Quarterly Interview Survey (Interview) and a Diary Survey (Diary).
Ensuring confidentiality prohibits publication of all, identifiable data inputs.
However, the BLS shares a sizeable sample of these sources, anonymized, called Public 
Use Microdata (PUMD).

## Concepts & Glossary

The Interview data has quarterly observations on each CU, while the Diary data is 
collected online bi-weekly.  So the PUMD datasets include a NEWID key that is the CU
identifier (CUID) suffixed by the observation. For interview data, the last digit 
ranges quarters (1,2,3,4) and for diary entries ranges biweek (1,2).

The PUMD includes a dimension of population density. First, CUs are split into Urban
vs Outside Urban. Urban CUs are then split into includes a categorical variable called
**popsize** or "Population Size Area" (PSA) which yields:
- Outside urban area
- All urban consumer units
- Less than 100,000
- 100,000 to 249,999
- 250,000 to 999,999
- 1,000,000 to 2,499,999
- 2,500,000 to 4,999,999
- 5,000,000 and more

The PUMD is published as sets of SAS, STAT or csv files.
This processing uses the csv file format.

The lowest level of detail collected in the PUMD is assigned a Universal
Classification Code (UCC), a six digit string left padded with zeros. The
BLS also uses these categories of spending for its Consumer Price Inflation (CPI)
publication.

For the PUMD, the UCC details are aggregated in to tree of subtotalling variables,
in a stucture called the hierarchical grouping (HG). The HG has three forms for the 
Interview, Diary and 'Integrated' view of the PUMD data. The lowest level nodes on the
HG are UCCs themselves. For example, the UCCs for cookies ('020510') and crackers 
('20610') are subtotaled to the variable "CRAKCOOK". 

At the highest level, the HG sums into four sections:
- Consumer unit characteristics like number of people, age of the reference person
- Demographics like race, ethnicity, education
- Incomes and Taxes
- Spending (finally) also called Average Annual Expenditures
This last, largest group of variables has its first level of detail such as Food,
Housing, Transportation and Health care.

The PUMD data is distributed by year, in quarterly files that have one of these formats:
  Diary Files
    FMLD - characteristics, income, weights, and summary level expenditures for the CU.
    MEMD - characteristics and income for each member in the CU.
    EXPD - a detailed weekly expenditure file categorized by UCC.
    DTBD - a detailed annual income file categorized by UCC.
    DTID - a Consumer Unit imputed income file categorized by UCC.
  Interview Files
    FMLI - characteristics, income, weights, and summary level expenditures for the CU.
    MEMI - characteristics and income for each member in the CU.
    MTBI - a detailed monthly expenditure file categorized by UCC.
    ITBI - a Consumer Unit monthly income file categorized by UCC.
    ITII - a Consumer Unit monthly imputed income file categorized by UCC.4
    NTAXI - a file with federal and state tax information for each tax unit in the CU.5

While these are many, the BLS shares some programming that focuses on just four. The
'family' data are keyed by Consumer Unit (CU) from each of the interview and diary sets
(FMLI & FMLD).  The UCC level spending details are found in (EXPD & MTBI)

---
## Bugs & Issues
- One year has two columns were lowercase
- In 2018, vars were renamed


---
## Citations
Public Use Microdata (PUMD) https://www.bls.gov/cex/pumd_data.htm


"""

import pandas as pd
import numpy as np
from datetime import datetime
import wget
import zipfile
import os
import warnings
warnings.simplefilter("ignore")

def oe_cex_pumd_download(years, pumddir = './pumd/', cexurl='https://www.bls.gov/cex/'):
    """
    This function downloads the files, dictionaries and hierarchical groupings of in
    Bureau of Labor Statistics (BLS), Consumer Expenditure Survey's (CEX) Public Use 
    Microsample Data (PUMD). Adjustments and corrections to this source are applied by
    the related oe_cex_pumd_read function.
        
    :param  years:    a list of 4 digit years that are strings like ['2018','2019','2020'] 
    :param  pumddir:  a string with the path destination of the download & unzipped files 
    :param  cexurl:   the root URL for the Consumer Expenditure Survey

    :return None   The function either succeeds or fails
    """
    
    # Avoid conflicts with any previously downloaded
    if os.path.exists(pumddir):
        print("Destination directory '"+pumddir+"already exists.")
        print("Please remove it or select a new destination directory.")
        raise
    else:
        os.mkdir(pumddir)

    # Download and reformat the HGs as a dictionary of dataframes
    for yr in years:
        for fn in ('diary','intrvw'):
            # download
            print('Downloading',yr,fn)
            wget.download(cexurl+'pumd/data/comma/'+fn+yr[2:]+'.zip',
                          out=pumddir,
                          bar=None)
            # unzip
            with zipfile.ZipFile(pumddir+fn+yr[2:]+'.zip', 'r') as zip_ref:
                zip_ref.extractall(pumddir)
            
    # also need the HG file.  It is a zip of all years.
    print('Downloading Hierarchical Grouping file')
    wget.download(CEXURL+'pumd/stubs.zip', 
                  out=PUMDDIR,
                  bar=None)
    with zipfile.ZipFile(PUMDDIR+'stubs.zip', 'r') as zip_ref:
        zip_ref.extractall(PUMDDIR)

    # Get the PUMD dictionary
    print('Getting the PUMD dictionary')
    wget.download(CEXURL+'pumd/ce_pumd_interview_diary_dictionary.xlsx',
                  out=PUMDDIR,
                  bar=None)

    return None

def oe_cex_pumd_open_files(years, pumddir = './pumd/'):
    """
    This function reads the PUMD data files of the dataset into python data structures. 

        
    :param  years: a list of 4 digit years that are strings     ['2018','2019','2020'] 
    :param  UCCs: a list of UCCs, six digit as strings     ['123456','234567','345678']

    pumdfiles: a dictionary, by year, with the file based dataframes
    hg: the Hierarchical Grouping table with linenum, level, title, survey, factor.
    vardict: provides a dictionary of the variables (not UCCs) in the PUMD
    codedict: provides a table with a description for each coded value in the PUMD

    :return  pumdfiles, hg, vardict, codedict
    """
    
    filetypes = ['dtbd','dtid','expd','fmld','memd','fmli','itbi','itii','memi','mtbi','ntax']

    filereads = {}
    for t in filetypes:
        filereads[t] = []

    for yr in years:
        for fn in ('diary','intrvw'):
            print("Reading",yr,fn)
            # Sometimes the intrv folder is in another subdir  intrvw17/intrvw17/*.csv eg
            if ((fn == 'intrvw') & (os.path.exists(pumddir+fn+yr[-2:]+ "\\"+fn+yr[-2:]+"\\"))):
                folder = fn+yr[-2:]+ "\\"+fn+yr[-2:]+"\\"
            else:
                folder = fn+yr[-2:]+ "\\"
            for f in os.listdir(pumddir+folder):
                ftype = f[0:4]
                if ftype in filetypes:
                    fdf = pd.read_csv(pumddir+folder +f, dtype=object)
                    fdf.columns = [c.upper() for c in fdf.columns]
                    fdf["filename"] = f
                    fdf["year"] = yr
                    filereads[ftype].append(fdf)
                    
        pumd = {}
        for t in filetypes:
            pumd[t] = pd.concat(filereads[t])   
    
    print('Reading the Hierarchical Groupings')
    # I'll use the Integrated HG.  Its mostly a superset of Interview & Diary HG less a dozen each
    hg = {}
    hgdtypes = {"linenum":int, "level":str, "title":str, "ucc":str, "survey":str, "factor":str, "group":str}
    for yr in years:
        h = pd.read_fwf(PUMDDIR+'stubs\\CE-HG-Integ-'+yr+'.txt', index_col=False,
        names = ["linenum", "level",  "title",  "ucc",     "survey",  "factor", "group"],
        colspecs = [(0, 3),  (3, 6),  (6, 69),  (69, 75),  (82, 85),  (85, 88), (88,95)],
        dtype=hgdtypes)    
        # Rows with linenum == 2 are just title text that wrapped from the previous row.
        for i,r in h.iterrows():
            if r.linenum == 2:
                h.at[i-1,'title'] = h.at[i-1,'title']+' '+r.title
        hg[yr] = h[h.linenum == 1]
     
    print('Reading the Dictionary')
    # The sheet names can varyin capitalization and include spaces
    xl = pd.ExcelFile(PUMDDIR + 'ce_pumd_interview_diary_dictionary.xlsx')
    varsheet =  [c for c in xl.sheet_names if 'vari' in c.lower()][0]
    codesheet = [c for c in xl.sheet_names if 'code' in c.lower()][0]

    vardict =   pd.read_excel(PUMDDIR + 'ce_pumd_interview_diary_dictionary.xlsx',
                              sheet_name = varsheet)
    codedict =  pd.read_excel(PUMDDIR + 'ce_pumd_interview_diary_dictionary.xlsx',
                              sheet_name = codesheet)

    # filter the vardict sheet to only those where 
    #     you year of interest is > First Year > First Quart and < Last Year <Last Quarter
    
    return  pumd, hg, vardict, codedict

def oe_cex_pumd_interpret_data(pumd, vardict, year):
    """
    This function applies adjustments, logical rules and corrections to this source
    are applied by the related oe_cex_pumd_read function.to PUMD data structures. 

    :param  years: a list of 4 digit years that are strings     ['2018','2019','2020'] 
    :param  UCCs: a list of UCCs, six digit as strings     ['123456','234567','345678']

    pumdfiles: a dictionary, by year, with the file based dataframes
    hg: the Hierarchical Grouping table with linenum, level, title, survey, factor.
    vardict: provides a dictionary of the variables (not UCCs) in the PUMD
    codedict: provides a table with a description for each coded value in the PUMD
    
    The processing logic replicates what the BLS' own SAS (& R) program does!
    See:    https://www.bls.gov/cex/pumd-getting-started-guide.htm
            https://www.bls.gov/cex/pumd/sas-ucc.zip
            https://www.bls.gov/cex/pumd/r-ucc.zip
            
    This is also helpful 
            https://www.bls.gov/cex/pumd_doc.htm
            https://www.bls.gov/cex/csxintvw.pdf

    :return family:  a dataframe keyed by CU (NEWID) 
    :return expend:  a dataframe keyed by CU & UCC 
    :return pubfile: a join between family, expend 
    """

    print("Processing PUMD for", year)

    # Get family dataframes for Interview and Diary
    fmli = pumd['fmli'][pumd['fmli'].year == year]
    fmld = pumd['fmld'][pumd['fmld'].year == year]
    # Get member level dataframes
    mtbi = pumd['mtbi'][pumd['mtbi'].year == year]
    expd = pumd['expd'][pumd['expd'].year == year]

    # column name lists
    wtrep = [("WTREP"+str(i+1).zfill(2)) for i in range(44)]+["FINLWT21"] ## WTREP01-REPWT444 and FINL
    repwt = [("REPWT"+str(i+1)) for i in range(45)]  # REPWT1-REPWT45
    rcost = [("RCOST"+str(i+1)) for i in range(45)]  # RCOST1-RCOST45

    # Process Family

    fmli["source"] = 'I'

    def mo_scope(row):
        if   (row["QINTRVMO"] in ['01','02','03']) & (row["QINTRVYR"]==year):
            return (int(row["QINTRVMO"]) - 1)
        elif (row["QINTRVMO"] in ['01','02','03']) & (row["QINTRVYR"]==str(int(year)+1)):
            return (4 - int(row["QINTRVMO"]))
        else:
            return 3

    fmli['mo_scope'] = fmli.apply(mo_scope, axis=1)

    for i in range(45):
        fmli[wtrep[i]] = fmli[wtrep[i]].astype(float).fillna(0)
        fmli[repwt[i]] = (fmli[wtrep[i]] * fmli["mo_scope"]) / 12

    fmld["source"] = "D"
    fmld["mo_scope"] = 3
    for i in range(45):
        fmld[wtrep[i]] = fmld[wtrep[i]].astype(float).fillna(0)    
        fmld[repwt[i]] = (fmld[wtrep[i]] * fmld["mo_scope"]) / 12

    fmli = fmli.reset_index()
    fmld = fmld.reset_index()
    fmlcols = ([c for c in fmli.columns if c in fmld.columns]) # 272 columns
    family = pd.concat([fmli[fmlcols],fmld[fmlcols]], axis=0)

    # Process flag fields   _ values of A,B,C are NAs
    print("Processing flag fields")
    def flag_NAs(row,flagged,flagcol):
        if row[flagcol] in ["A","B","C"]:
            return np.NaN
        else:
            return row[flagged]
        return None

    flags = {}
    flag_candidates = vardict[["Variable Name","Flag name"]][~vardict["Flag name"].isna()].drop_duplicates()
    for i,r in flag_candidates.iterrows():
        if (r["Variable Name"] in family.columns) & (r["Flag name"] in family.columns):
            flags[r["Variable Name"]] = r["Flag name"]

    for col in flags.keys():
        print("    ",col,"flagged by",flags[col])
        family[col[:-1]] = family.apply(lambda row: flag_NAs(row,col,flags[col]), axis=1)

    family.drop([c for c in flags.values()], axis=1, inplace=True)
    fmlcols = family.columns  # reset this list

    # Process Expend

    mtbi["source"] = "I"
    mtbi = mtbi[(mtbi["REF_YR"] == year) & (mtbi["PUBFLAG"] == "2")]

    expd["source"] = "D"
    expd["COST"] = pd.to_numeric(expd["COST"], errors='coerce')
    expd["COST"] = expd["COST"].astype(float).fillna(0) * 13
    expd = expd[expd["PUB_FLAG"] == "2"]

    expcols =['NEWID','source','UCC','COST'] #,'REF_YR'
    expend = pd.concat([mtbi[expcols],expd[expcols]], axis=0)

    pubfile = pd.merge(family, expend, on='NEWID', how='inner')
    pubfile["COST"] = pubfile["COST"].astype(float).fillna(0)
    for i in range(45):
        pubfile[rcost[i]] = pubfile[wtrep[i]] * pubfile["COST"]
    return pubfile, family, expend

def oe_cex_pumd_interpret_meta(hg,vd,cd,year):

    print("Narrowing metadata to", year)
    
    # Interpret the Hierarchical Grouping
    
    # survey column:
    #    I: Interview survey
    #    D: Diary survey
    #    G and T: Titles
    #    S: Statistical UCCs

    # group column
    #    CUCHARS: CU characteristics
    #    FOOD: Food expenditures
    #    EXPEND: Non-food expenditures
    #    INCOME: Income types
    #    ASSETS: Asset types
    #    ADDENDA: Other financial information and gifts
    h = hg[year]
    
    # Interpret the Var Dictionary
    vd["Last year"] = vd["Last year"].fillna(datetime.now().year)
    v = vd[(int(yr) >= vd["First year"] ) & (int(yr) <= vd["Last year"] )]
    
    # Interpret the Code Dictionary
    cd["Last year"] = cd["Last year"].fillna(datetime.now().year)
    c = cd[(int(yr) >= cd["First year"] ) & (int(yr) <= cd["Last year"] )]
    
    return h,v,c


def oe_cex_pumd_write(df, year):
    """
    This function writes a final dataframe to file.
    """
    print("Writing to "+year+" blockgroupspending file")
    df.to_csv(year+'blockgroupspending.csv', index=False)
    return None


if __name__ == "__main__":
    
    # Capitalized variables are globals or multi-year storage
    # Lowercase variables are those for a given working year
    
    CEXURL = 'https://www.bls.gov/cex/'
    PUMDDIR = "D:\\Open Environments\\data\\bls\\cex\\pumd\\"
    YEARS = ["2018"] # ['2016','2017','2018','2019','2020']
    
    #oe_cex_pumd_download(YEARS, pumddir = PUMDDIR, cexurl=CEXURL)
    
    PUMD, HG, VARDICT, CODEDICT = oe_cex_pumd_open_files(YEARS, pumddir = PUMDDIR)
    
    for yr in YEARS: 
        hg, vardict, codedict    = oe_cex_pumd_interpret_meta(HG,VARDICT,CODEDICT,yr)
        pubfile, family, expend  = oe_cex_pumd_interpret_data(PUMD,VARDICT,yr)
        oe_pumd_write(family,yr)
        print(yr,family.shape)

    # WTREP & REPWT   90 weighting columns
    

    # family.CUID & family.NEWID 
    
    # family.POPSIZE

    # family.DIVISION
    states = pd.read_csv("https://raw.githubusercontent.com/OpenEnvironments/core/main/states.csv")
    divisions = states[['CensusDivisionName','CensusDivisionCode']].drop_duplicates().dropna()

    # family.
    print("Done")
