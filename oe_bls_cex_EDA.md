# Bureau of Labor Statistics,
## Consumer Expenditure Survey
### Exploratory Data Analysis (EDA)
---
### Overview
---
The Bureau of Labor Statistics (BLS) is charged by the US Congress to estimate details of consumer spending for public use, and to support various agencies charged with economic analysis. The BLS Consumer Expenditure Survey (CX or CEX) is intended to make estimates at the national level. The survey is updated once a year.

The full publication includes various summary reports with additional estimation for selected states (40) and selected cities (24 MSAs). The CEX also includes anonymized detail for research including its Public Use Microdata (PUMD) files and Time Series files to support access by API.

### Key Concepts
---
* The survey is addressed to a **Consumer Unit (CU)** which is very similar to a Census household. **Members** of a CU would include **Reference Person** responsible for the amounts reported as well as a "2" person, such as a spouse.

* ***UCC, Item, Subcategory, Category*** The Survey collects original data by Universal Classification Codes (UCCs) with 6 digit identifiers. These basic variables are subtotaled up through a consolidation tree called a Hierarchical Grouping. Together, UCCs and subtotalling variables are called Items. Finally, Items are added to a level total called a Subcategory wich are grouped together in Categories. So:
    Category: Expenditure
        Subcategory: Food (FOODTOTL)
            Food at home (FOODHOME)
                Cereals and bakery products (CERBAKRY)
                    Bakery products (BAKERY)
                        Other bakery products OTHBAKRY
                            Cakes and cupcakes (020410)

* ***Weights*** In its survey design, the BLS applies stratified sampling to ensure each consumer category (geography, race, age, income, etc.) is sufficiently represented. As a result, the profile of the consumers selected in the Interviews and Diary do not reflect the US distribution. As a result, the BLS calculates a weight for each source observation that represents the number of CUs in the total U.S. population that it represents.  To get to this weight, the BLS applies Balanced Repeated Replication (BRR) generating 44 sampling attemps stored in the variables named **WTREP01 - WTREP44**. The final weight, **FINLWT21** is relevant, while the WTREP weights can be ignored. The FINLWT21 is intended to weight the quarterly or biweekly observation up to an annual basis.

* ***PSU, MSA, CBSA*** The Survey is designed to estimate just the national level of geography, but it includes estimates for a select, largest set of States and MSAs. For the survey, the "primary sampling unit" (PSU) is the major MSA. The US Office of Management of Budget (OMB) administers the codes for Metropolitan, Miccropolitan and Combined statistical areas. However, the BLS has its own coding that it shares between the CEX survey and its Consumer Price Inflaction (CPI) publications. So, the **oe_bls** python module includes a reference file that maps CEX PSU codes and names to OMB MSA codes and names. **2018 Update:** In 2018, the BLS changed its geographic structures from MSAs to CBSAs https://www.bls.gov/cpi/additional-resources/geographic-revision-2018.htm. The OMB defines a metropolitan statistical area (MSA) as a core-based statistical area having at least one urbanized area of 50,000 or more population, plus adjacent territory that has a high degree of social and economic integration with the core as measured by commuting ties. Citation: https://data.nber.org/cbsa-csa-fips-county-crosswalk/cbsa2fipsxw.csv

There are 3,006 counties in the US including County Equivalents: DC, Louisiana "parishes", Alaska "Census Areas", Connecticut "Councils of Government" and New England City and Town Areas (NECTAs). Counties provide the demographic basis for "Statistical Areas".

About two thirds of US counties (1916), are considered **Core Based Statistical Areas (CBSA)**, a fancy name for a city.
    CBSA 10140 for Aberdeen, WA is a **Micropolitan Statistical Area**. It has 1 county Grays Harbor County.
    CBSA 27540 for Jasper, IN is a Micropolitan Statistical Area with 2 counties (Dubois and Pike)
        When a CBSA spans multiple counties, one is considered "Central" and the others "Outlying"
    CBSA 13820 for Birmingham, AL is large enough to be called a **Metropolitan Statistical Area** with 2 counties.
    CBSA 41860 for San Francisco-Oakland-Hayward, CA is a Metro Stat Area.  However, its counties are considered Micropolitan in
        their own right, so its counties (Alameda and Contra Costa) are given their own CBSA codes called **Metropolitan Divisions**.
            Metro Divisions also have 5 digit codes that ARE NOT CBSAs.
Finally, the largest CBSAs, major cities (between 160-180), are called **Combined Statistical Areas**. These each have a three digit codeand include the likes of Los Angeles, New York, Dallas and Chicago.

* ***POPSIZE, URBN*** The PUMD includes 2 dimensions of population density. BLS_URBN provides a flag, made by the Bureau, that categorizes urban vs rural geographies. POPSIZE aka "Population Size Area" (PSA) provides 5 categories of each MSA. POPSIZE value 1-3 are entirely urban, while popsize 4-5 are split urban and rural. Together they provide a joint category of 7 types of population density.

---
## PUMD
Ensuring confidentiality prohibits the Bureay from publishing of all, identifiable data inputs. However, the BLS shares a sizeable sample of these sources, anonymized, called the Public Use Microdata (PUMD).

* ***Interviews and Diaries*** The Consumer Expenditure Survey represents national estimates based upon two original
data collections: a Quarterly Interview Survey (Interview) and a Diary Survey (Diary). The Interview data has quarterly observations on each CU, while the Diary data is collected online bi-weekly. So the PUMD datasets include a NEWID key that is the CU identifier (CUID) suffixed by the observation. For interview data, the last digit of the NEWID ranges quarters (1,2,3,4) and for diary entries it ranges biweekly (1,2).

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

* ***Family, Expend*** While these are many, the BLS shares some programming that focuses on just four. The ***Family*** data are named fmli,fmld, with one each of the interview and diary collections. The ***Expend*** files are found in EXPD & MTBI.  A ***Pubfile** is a join between these.
* ***X,M,B,I*** are suffixed to a variable to indicate that the variable is "as collected", "collected or imputed","bracketed".  The imputed form of the variable addresses missed or accidental entries so it is preferred.  The bracketed form makes the quantitative original into categories. The I suffix refers to the method of imputing that yielded the imputed form.
* ***1,2,3,4,5*** are suffixed to a variable to show incremental rounds of imputation attempts. The original variable name is final, so the imputation rounds can be ignored.
* ***CQ,PQ*** are appended to an internview variable to indicate that it reflects the current quarter or previous quarter, respectively. The previous quarter may refer to a previous year's collection entirely, and may not reflect the amount actuall recorded in the CU's previous observation. So, current quarter is preferred and previous quarter can be ignored.
* ***_REF,2*** are appendied to variables like SEX, EDUC and AGE to describe that of the reference person and their spouse respectively.
* ***Weights*** FINL21 contains the final weight amount selected for that NEWID.

---
## Exploratory Data Analysis

* The CEX estimates are based upon two original data collections: a Quarterly Interview Survey (**Interview**) and a Diary Survey (**Diary**). The Interview is fielded quarterly while the Diary is done over 2 consecutive weeks. For a given observation year, the 4 quarter responses may be collected well into the first quarter of the following year.
* Ensuring confidentiality prohibits publication of all, identifiable data inputs. However, the BLS shares a sizeable sample of these sources, anonymized, called the **Public Use Microdata (PUMD)** dataset.


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


### Hierarchical Grouping (HG)

The CEX Survey prompts participants to report spending on detailed variables (UCCs).
These are then subtotaled up to intermediate summary variables (FOOD, eg) and
ultimately to TOTEXP.

Hierarchical Group refers to this summary tree where the leaves are UCCs and the 
nodes are variable names. The BLS offers three alternative views of this summary:
"Diary", "Interview" and "Integrated".  

The Hierarchical Grouping is downloaded as a single zip file that unzips into folder
of fixed column width text files, for each year and each alternative summary. For
example, the file named CE-HG-Diary-2020 provides the 2020 version of Diary groupings.

Each file includes 7 columns:

    "linenum":int   is all 1s except when the title text needs to wrap. Its a 2 when the row
                    provides extra title text to be appended to the 1 row above it.
                    
    "level":int     Refers to the level of that variable in the grouping tree. A level 3
                    variable followed by level 4 rows would indicate the parent child
                    relationship until the next level 3 is encountered.
                    
    "title":str     Provides the description of the variable.

    "ucc":str       Provides the UCC or variable name.
    
    "survey":str    Sets the source survel that collected that variable:
                        I: Interview survey
                        D: Diary survey
                        G and T: Titles
                        S: Statistical UCCs

    "category":str  Defines the highest level category for each variable
                        CUCHARS: CU characteristics
                        FOOD: Food expenditures
                        EXPEND: Non-food expenditures
                        INCOME: Income types
                        ASSETS: Asset types
                        ADDENDA: Other financial information and gifts

### Variable and Code Dictionaries

Variable pairs ending in [CQ,PQ] refer toe [Current Quarter, Previous Quarter]. Prefer the former.

Variable pairs ending in [X,M] are either ["as collected","as collected or imputed"]. Prefer the latter.


### FMLI
This is the main family interview data, with up to 4 quarterly observations per CUID.

### FMLD




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
