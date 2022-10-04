#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
The US Bureau of Labor Statistics publishes the Pubmic Use Microdata (PUMD) to support
deeper analysis of its Consumer Expenditure Survey. This module provides functions for 
downloading PUMD data and its metadata. It also applies business rules for interpreting
this dataset.
    
    oe_bls_cex_pumd_download          - retrieves the PUMD files from the BLS to a new folder
    oe_bls_cex_pumd_open_files        - opens the downloaded files into python dataframes
    oe_bls_cex_pumd_interpret_meta    - selects a request year of the Variable Dictionary and Historical Grouping
    oe_bls_cex_pumd_interpret_data    - applies rule to combine the FMLI, FMLD, MTBI and EXPD files
        oe_bls_cex_pumd_flags         - applies flag column rules to fmli, fmld
        oe_bls_cex_pumd_select        - For fmli & fmld, this selects demog, geog and expenditure cols of interest
    oe_bls_cex_pumd_write             - stores the resulting data structures to pcikle files

The final section of this files demonstrates these functions for working examples.

"""

import pandas as pd
import numpy as np
from datetime import datetime
import wget
import zipfile
import os
import warnings
warnings.simplefilter("ignore")

def oe_bls_cex_pumd_download(years, pumddir = './pumd/', cexurl='https://www.bls.gov/cex/'):
    """
    This function downloads the files, dictionaries and hierarchical groupings of in
    Bureau of Labor Statistics (BLS), Consumer Expenditure Survey's (CEX) Public Use 
    Microsample Data (PUMD).
        
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
    wget.download(cexurl+'pumd/stubs.zip', 
                  out=pumddir,
                  bar=None)
    with zipfile.ZipFile(pumddir+'stubs.zip', 'r') as zip_ref:
        zip_ref.extractall(pumddir)

    # Get the PUMD dictionary
    print('Getting the PUMD dictionary')
    wget.download(cexurl+'pumd/ce_pumd_interview_diary_dictionary.xlsx',
                  out=pumddir,
                  bar=None)

    return None

def oe_bls_cex_pumd_open_files(years, pumddir = './pumd/'):
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
        
    pumd = {}
    
    for yr in years:
        pumd[yr] = {}
        for fn in ('diary','intrvw'):
            print("Reading",yr,fn)
            # Sometimes the intrv folder is in another subdir:  intrvw17/intrvw17/*.csv eg 
            if ((fn == 'intrvw') & (os.path.exists(pumddir+fn+yr[-2:]+ "\\"+fn+yr[-2:]+"\\"))):
                folder = fn+yr[-2:]+ "\\"+fn+yr[-2:]+"\\"
            else:
                folder = fn+yr[-2:]+ "\\"
            for f in os.listdir(pumddir+folder):
                ftype = f[0:4]
                if ftype in filetypes:
                    fdf = pd.read_csv(pumddir+folder+f, dtype=object)
                    fdf.columns = [c.upper() for c in fdf.columns]
                    fdf["filename"] = f
                    fdf["year"] = yr
                    filereads[ftype].append(fdf)

        for t in filetypes:
            pumd[yr][t] = pd.concat(filereads[t])   
    
    print('Reading the Hierarchical Groupings')
    # I'll use the Integrated HG.  Its mostly a superset of Interview & Diary HG less a dozen each
    hg = {}
    hgdtypes = {"linenum":int, "level":str, "title":str, "ucc":str, "survey":str, "factor":str, "group":str}
    for yr in years:
        h = pd.read_fwf(pumddir+'stubs\\CE-HG-Integ-'+yr+'.txt', index_col=False,
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
    xl = pd.ExcelFile(pumddir + 'ce_pumd_interview_diary_dictionary.xlsx')
    varsheet =  [c for c in xl.sheet_names if 'vari' in c.lower()][0]
    codesheet = [c for c in xl.sheet_names if 'code' in c.lower()][0]

    vardict =   pd.read_excel(pumddir + 'ce_pumd_interview_diary_dictionary.xlsx',
                              sheet_name = varsheet)
    codedict =  pd.read_excel(pumddir + 'ce_pumd_interview_diary_dictionary.xlsx',
                              sheet_name = codesheet)

    # filter the vardict sheet to only those where 
    #     you year of interest is > First Year > First Quart and < Last Year <Last Quarter
    
    return  pumd, hg, vardict, codedict

def oe_bls_cex_pumd_interpret_data(pumd, vardict, year, sumrules):
    """
    This function applies adjustments, logical rules and corrections to this source
    are applied by the related oe_bls_cex_pumd_read function.to PUMD data structures. 

    :param  years: a list of 4 digit years that are strings     ['2018','2019','2020'] 
    :param  UCCs: a list of UCCs, six digit as strings     ['123456','234567','345678']

    pumdfiles: a dictionary, by year, with the file based dataframes
    hg: the Hierarchical Grouping table with linenum, level, title, survey, factor.
    vardict: provides a dictionary of the variables (not UCCs) in the PUMD
    sumrules: a dataframe of each summary variable name, summary level and list of children 
            columns to sum

    The processing logic replicates what the BLS' own SAS (& R) program does!
    See:    https://www.bls.gov/cex/pumd-getting-started-guide.htm
            https://www.bls.gov/cex/pumd/sas-ucc.zip
            https://www.bls.gov/cex/pumd/r-ucc.zip
            
    This is also helpful 
            https://www.bls.gov/cex/pumd_doc.htm
            https://www.bls.gov/cex/csxintvw.pdf

    :return family:  a dataframe keyed by NEWID
    :return expend:  a dataframe keyed by CU & UCC 
    :return pubfile: a join between family, expend 
    """

    print("Processing PUMD for", year)

    # Get family dataframes for Interview and Diary
    fmli = pumd[year]['fmli']
    fmld = pumd[year]['fmld']
    # Get member level dataframes
    mtbi = pumd[year]['mtbi']
    expd = pumd[year]['expd']

    # column name lists
    wtrep = [("WTREP"+str(i+1).zfill(2)) for i in range(44)]+["FINLWT21"] ## WTREP01-REPWT444 and FINL
    repwt = [("REPWT"+str(i+1)) for i in range(45)]  # REPWT1-REPWT45
    rcost = [("RCOST"+str(i+1)) for i in range(45)]  # RCOST1-RCOST45

    # Process Family

    def mo_scope(row):
        if   (row["QINTRVMO"] in ['01','02','03']) & (row["QINTRVYR"]==year):
            return (int(row["QINTRVMO"]) - 1)
        elif (row["QINTRVMO"] in ['01','02','03']) & (row["QINTRVYR"]==str(int(year)+1)):
            return (4 - int(row["QINTRVMO"]))
        else:
            return 3

    fmli['mo_scope'] = fmli.apply(mo_scope, axis=1)
    fmli["source"] = 'I'
    for i in range(45):
        fmli[wtrep[i]] = fmli[wtrep[i]].replace('.',np.nan)
        fmli[wtrep[i]] = fmli[wtrep[i]].astype(float).fillna(0)
        fmli[repwt[i]] = (fmli[wtrep[i]] * fmli["mo_scope"]) / 12

    fmld["source"] = "D"
    fmld["mo_scope"] = 3
    for i in range(45):
        fmld[wtrep[i]] = fmld[wtrep[i]].replace('.',np.nan)
        fmld[wtrep[i]] = fmld[wtrep[i]].astype(float).fillna(0)    
        fmld[repwt[i]] = (fmld[wtrep[i]] * fmld["mo_scope"]) / 12

    fmli = fmli.reset_index()
    fmld = fmld.reset_index()
    
    oe_bls_cex_pumd_process_flags(fmli,"FMLI",vardict)
    oe_bls_cex_pumd_process_flags(fmld,"FMLD",vardict)

    fmlcols = ([c for c in fmli.columns if c in fmld.columns]) # 272 columns
    family = pd.concat([fmli[fmlcols],fmld[fmlcols]], axis=0)
    
    
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
        
    #
    # TBD: summarize the pubfile, and apply the sumrules
    #
    
    # 1. Start with a df that has CUID/NEWID, COST and UCC columns
    # 2. Pivot this df so there's a column for each UCC value
        # costs = df.pivot(index='NEWID', columns='UCC', values='COST')
    # 3. Ensure that all the expected UCC columns are present
    #   # for all the UCC variables, if the cost df is missing that var, costs[missingUCC] = 0
    # 4. March from the lowest level upward
        # for level in [9,8,7,6,5,4,3,2]:
    #   costs[sumvar] = costs[sumrulescolumns].sum(axis=1)
        
    return pubfile, family, expend, fmli, fmld, mtbi, expd


def oe_bls_cex_pumd_flag_NAs(row,flagged,flagcol):
    """
    Process flag fields ensuring A,B,C are NAs
    Called by the oe_bls_cex_pumd_process_flags
    Initially this is a simple rule, but this function provides a placeholder
    for more complex use of the PUMD Variable Dictionary 
    """
    if row[flagcol] in ["A","B","C"]:
        return np.NaN
    else:
        return row[flagged]
    return None


def oe_bls_cex_pumd_process_flags(df,filename,vd):
    """
    PUMD variables may be accompanied by a sister flag column that indicates
    how missing and top/bottom coded values should be handled.
    This function applies flag rules to a dataframe then drops the flag columns.
    """
    print("Processing flags for",filename)
    flags = {}
    flag_candidates = vd[["Variable Name","Flag name"]][~vd["Flag name"].isna()][vd["File"] == filename].drop_duplicates()
    for i,r in flag_candidates.iterrows():
        if (r["Variable Name"] in df.columns) & (r["Flag name"] in df.columns):
            flags[r["Variable Name"]] = r["Flag name"]
    for col in flags.keys():
        print("    ",col,"flagged by",flags[col])
        df[col[:-1]] = df.apply(lambda row: oe_bls_cex_pumd_flag_NAs(row,col,flags[col]), axis=1)
    df.drop([c for c in flags.values()], axis=1, inplace=True)
    return df


def oe_bls_cex_pumd_interpret_meta(hg,vd,cd,year):

    print("Narrowing metadata to", year)
    
    # Interpret the Hierarchical Grouping
    h = hg[year]
    
    # Generate the summarization rules from HG
    h["level"] = h["level"].astype(int)
    sumdict = {}
    sumrules = {}
    for level in [9,8,7,6,5,4,3,2]:
        for i,g in h[h.level.isin([level, level-1])].iterrows():        
            if g.level == level-1:
                rule = g.ucc
                sumdict[rule] = level-1
                sumrules[rule] = []
            else:
                sumrules[rule].append(g.ucc)

    emptyrules = [r for r in sumrules.keys() if len(sumrules[r]) == 0]
    for rule in emptyrules:
        sumrules.pop(rule)
        sumdict.pop(rule)

    # Test the rules
    for rule in sumrules.keys():
        if (len(sumrules[rule]) > 0) & (rule.isnumeric()):
            print('invalid rule',rule,': members but numeric')
        if (len(sumrules[rule]) == 0) & (not rule.isnumeric()):
            print('invalid rule',rule,': no members but not numeric')
    # the rule level is needed so they can be applied bottom up
    r = pd.DataFrame.from_dict({'name':  list(sumdict.keys()),
                                'level': [sumdict[r] for r in sumdict.keys()],
                                'rule':  [sumrules[r] for r in sumdict.keys()]})    
    
    # Interpret the Var Dictionary
    vd["Last year"] = vd["Last year"].fillna(datetime.now().year)
    v = vd[(int(year) >= vd["First year"] ) & (int(year) <= vd["Last year"] )]
    
    # Interpret the Code Dictionary
    cd["Last year"] = cd["Last year"].fillna(datetime.now().year)
    c = cd[(int(year) >= cd["First year"] ) & (int(year) <= cd["Last year"] )]
    
    return h,r,v,c


def oe_bls_cex_pumd_write(df, year):
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
    YEARS = ['2018'] #['2016','2017','2018','2019','2020']
    
    oe_bls_cex_pumd_download(YEARS, pumddir = PUMDDIR, cexurl=CEXURL)
    
    PUMD, HG, VARDICT, CODEDICT = oe_bls_cex_pumd_open_files(YEARS, pumddir = PUMDDIR)
    
    for yr in YEARS: 
        hg, sumrules, vardict, codedict    = oe_bls_cex_pumd_interpret_meta(HG,VARDICT,CODEDICT,yr)
        pubfile, family, expend, fmli, fmld, mtbi, expd  = \
            oe_bls_cex_pumd_interpret_data(PUMD,VARDICT,yr,sumrules)
        oe_bls_cex_pumd_write(family,yr)

    print("Done")
