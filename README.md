<<<<<<< HEAD
## blockgroupspending
---
U.S. Consumer Expenditures by Census Block Groups
### Opportunity
---
Americans express themselves in many ways, but critically in their 
*income* and *spending* decisions. In th United States, the Bureau of Labor Statistics (BLS) is
responsible for publishing its Consumer Expenditure Survey (https://www.bls.gov/cex/).
This publication provides national level estimates in addition to select states
and select 25 largest MSAs. This level of geography often renders the estimates overly 
aggregated, limited to for microeconomic analysis and geography appending.

The BLS also provides a sample of the original survey responses to allow lower level
modelling. Its Public Use Microdata (PUMD) does not include geography, to protect the
respondent's confidentiality. However it does provide much more detail, and much more
complexity, which can support modelling across geographies.

This dataset applies two models to project consumer expenditures over smaller
Census geographies called Block Groups. Block Groups can range in size from about 600
to 3,000 residents in size. With Block Group codes, CEX spending can be merged with the
full range of Census estimates in either the American Community Survey or Decennial
publications.

The first of the projection models distributes the US and State totals down to Block Groups, 
so each begins with a total consumer spending amount. The second model predicts the 
allocation of a Block Group's total across spending categories.

The resulting dataset is keyed by Block Group GEOID with spending categories as columns.
The dataset is published on Harvard's dataverse at https://dataverse.harvard.edu/.  The
models' source are kept under version control in Open Environments repository at
https://github.com/orgs/OpenEnvironments/blockgroupspending

### Key Concepts
A BLS **Consumer Unit (CU)** refers to a group of people like to a Census Household.
Technically, a CE includes families, roommates and other people who make group
based spending decisions. 

Each Consumer Unit may have several **members** but each identifies a **Reference Person**
who is responsible for paying housing costs and acts as a point of contact.

The Survey provides estimates The MSA level of the CE publication is appropriately called 'select MSA' in that 
only the largest MSAs are involved.

Metropolitan Statistical Areas represent city geographies that may span both states and counties. The US Office
of Management and Budget (OMB) defines 384 of these, but the BLS only uses a select two dozen largest cities.

Survey participants sometimes respond with a singe purchase of two items. A person might purchase a shirt and
some health items from a pharmacy. The BLS then needs to **allocate** the amount into separate variables.

When selecting survey participants, the BLS uses stratified random sample. A simple random sample might
have insufficient observations of race, age or family type. So, the BLS ensures a minimum occurrence of
participants in these minority groups. This practice, however, means that the final collection does not 
reflect the total population distributions. The solution is to add a **weight** to each input that represents
the number of households that the input represents.


## Code
- *MSA* downloads and combines the MSA level spreadsheets, by region, with states as columns in each.
- *PUMD* downloads, reads and interprets the PUMD datasets by year.
- *models* contains the projection and penetration models, applies them and writes results to csv file.
=======
# oe_bls
---
The U.S. Bureau of Labor Statistic (BLS) publishes several surveys that integrate Census and Economic subjects.
This python module provides functions to access those surveys and the dimensions that support them.

---
## Consumer Expenditure Survey
---
The BLS is required by 





---
## Consumer Price Index

For each spending category, the BLS estimates average prices to calculate price inflation in detail.

>>>>>>> 1af90dd871048042d84b92f8c788230b8cc6ec53

