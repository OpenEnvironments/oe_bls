# Bureau of Labor Statistics,
# Consumer Expenditure Survey
# Exploratory Data Analysis (EDA)
---
## Overview


---
## Key Concepts

*Consumer Unit*

*Weights*
In its survey design, the BLS applies stratified sampling to ensure each consumer category (geography, race, age, income, etc.) is sufficiently represented. In this method, each CU included in the CE sample represents a given number of CUs in the U.S. population

---
## PUMD

---
## Exploratory Data Analysis
### Univariate



## Overview
---

The Consumer Expenditure Survey represents national estimates based upon two original
data collections: a Quarterly Interview Survey (*Interview*) and a Diary Survey (*Diary*).
Ensuring confidentiality prohibits publication of all, identifiable data inputs.
However, the BLS shares a sizeable sample of these sources, anonymized, called Public 
Use Microdata (PUMD).

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

The Survey intends to estimate the national population so summing across CUs should
reflects *weighting* where each CU represents a different fraction of the total pop. 

(to complicate things) 
Rather than one weight for each CU, the Survey uses Balanced Repeated Replication (BRR),
where the weight is re-estimated 45 times. The column named "FINLWTyy" is the final weight
for that yy year across weighting attempts (WTREP1-44).  Then, each attempt to estimate
population (REPWT) and cost (RCOST) and cost/pop and c/p per UCC has to reflect the 45
original weighting attempts.

Why not use the FINLWTyy to get single estimates of each?!

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
            https://www.ilo.org/surveyLib/index.php/catalog/1193/download/8310


---
## Bugs & Issues
- One year has two columns were lowercase
- In 2018, vars were renamed


---
## Citations
Public Use Microdata (PUMD) https://www.bls.gov/cex/pumd_data.htm
U.S. Department of Labor, Bureau of Labor Statistics, Consumer Expenditure Survey, 
  Interview Survey, 2013.
https://www.bls.gov/cpi/additional-resources/geographic-sample.htm


    # Geography:
    # family.PSU  is the primary sampling unit - for CEX that is an MSA!
    # CUs are intended to be weighted samples of an MSA
    #      An Metropolitan Statistical Area (MSA) is a subset of OMB's 
    #          Core Based Statistical Areas CBSA's
    #      Each MSA has a POPSIZE (the CU popsize is the MSA's replicated across CU records)
    #      Each MSA aggregates a group of counties (which can decompost into Census geogs)
    #          https://www.nber.org/research/data/census-core-based-statistical-area-cbsa-federal-information-processing-series-fips-county-crosswalk
    #      But BLS codes the MSAs using "CPI codes"  
    #          https://www.bls.gov/cpi/additional-resources/geographic-sample.htm
    #      National Bureau of Economic Research | NBER
    #          https://back.nber.org/appendix/c14245/replication/rawData/CPI%20MSA%20to%20Unemployment%20(OMB)%20MSA.xlsx
    #        
    # BOS Balance-of-State area codes are for areas in a US State that are OUTSIDE the major MSA
    # bls CPI Codes for MSA, bls QCEW survey codes the major MSAs with 
    # Office of Management and Budget
    #    these are repeated described as groups of counties
    #    so Block Groups can be married up to them
    # family.PSU.value_counts()
    #    S12A    2280
    #    S49A    1815
    #    S23A    1010
    #    S37A     704
    #    S35A     701

    # family.CUID identifies the household
    # family.NEWID identifies the data coll obs (several per household)
    # So:
    #    NEWID = "0" + CUID + [1,2,3,4] for quarterly interview or [1,2] for biweekly
    #    fmli.CUID.str.zfill(7) == fmli.NEWID.str[:-1]
    
    # family.FINLWT21
    
    # family.RACE_REF
        #1	White    32627
        #2	Black     4186
        #3	Native American      182
        #4	Asian     2083
        #5	Pacific Islander      127
        #6	Multi-race      656

    # family.STATE is FIPS codes of 40 states
    
    # family.POPSIZE
        #- 1	More than 5 million     8781
        #- 2	1-5 million    13917
        #- 3	0.5-1.0 million    4857
        #- 4	100-500 thousand     7971
        #- 5	Less than 100 thousand     4335

    # family.BLS_URBN  is related to POPSIZE, splitting level 4 and 5 into Urban Rural
        #        		BLS_URBN	1	2
        #    POPSIZE		
        #    	1					8781	0
        #    	2					13917	0
        #    	3					4857	0
        #    	4					7365	606
        #    	5					2269	2066


    # family.DIVISION refers to Census divisions grouping states (east, south, midwest, west)


    # family.MARITAL
        #1	Married    20730
        #2	Widowed     3770
        #3	Divorced     6133
        #4	Separated      911
        #5	Never married     8317
        
    # pubfile
    # Top Line Tables 2021 
    # https://www.bls.gov/cex/tables/calendar-year/mean/cu-all-multi-year-2021.pdf
    #     Number of CUs 133.595 million
    #     Income before taxes $87.432 m
    #     Income after taxes 78.743 m
    #     Race: African American or black 13%
    #     Hispanic or Latino: 15
    #     Educ of reference person 69 college
    #     Average annual expenditure $66,928 m   PER CU
    #
    #     Total spending CUs x Ave Annual = $8,941,246,160,000 

    # family.EDUC_REF
    #  46.7% have 14/15/16 college degree or greater
    #  00	Never attended                                   109
    #  10	Nursery, kindergarten, and elementary (grades 1-8)  1200
    #  11	High school (grades 9-12), no degree             2694
    #  12	High school graduate                             8880
    #  13	Some college, no degree                          8366
    #  14	Associate's degree in college                    4060
    #  15	Bachelors degree                                 9123
    #  16	Masters, professional or doctorate degree        5429
    
    # family.CUTENURE
    #   1	Owned w/mortgage                     14988
    #   2	Owned w/o mortgage                   10477 
    #   3	Owned mortgage NR                    210
    #   4	Rented                               13391
    #   5	Occupied w/o payment of cash rent    607
    #   6	Student housing                      188

    # family.CHILDAGE
    #    0	No children                                25266
    #    1	Oldest child less than 6                   2137
    #    2	Oldest child age 6-11 and at less one child less than 6       1374  
    #    3	All children age 6-11                      1448
    #    4	Oldest child age 12-17 and at less one child less than 12     1926
    #    5	All children age 12-17                       1963
    #    6	Oldest child age greater than 17 and at less one child less than 17   1569
    #    7	All children age greater than 17             25266

    
    # family.FAM_TYPE
    # 9522     1	Married Couple only
    # 1534     2	Married Couple, own children only, oldest child < 6           
    # 4431     3	Married Couple, own children only oldest child >= 6, <= 17
    # 2818     4	Married Couple, own children only, oldest child > 17
    # 1540     5	All other Husband and wife families
    #  394     6	One parent, male, own children at least one age < 18
    # 1583     7	One parent, female, own children, at least one age < 18
    # 12050    8	Single consumers
    # 5989     9	Other families   
    #
    # Corresponds to ACS
    #     Family = Married-couple vs Other family
    #
    # B11003e1 Families (basis)
        # B11003e2 Married-couple family
            # B11003e2 Married-couple family	With own children of the householder under 18 years
                # B11003e4 Married-couple family	With own children of the householder under 18 years	Under 6 years only
                # B11003e5 Married-couple family	With own children of the householder under 18 years	Under 6 years and 6 to 17 years
                # B11003e6 Married-couple family	With own children of the householder under 18 years	6 to 17 years only
            # B11003e7 Married-couple family	No own children of the householder under 18 years
    # B11003e8 Other family
        # B11003e9 Other family Male householder no spouse present
            # +  No own children, Own children under 18, Under 6, etc
        # B11003e15 Other family Female householder no spouse present
            # +  No own children, Own children under 18, Under 6, etc
        

*Balanced Repeated Replication (BRR)*
        # WTREP & REPWT   90 weighting columns


*Hierarchical Grouping*
Provides a tree, consolidating the original 
# 
# level column:

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
