#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
# oe_bls_cex_API
## Overview
The Bureau of Labor Statistics (BLS) publishes data in a variety of channels, including APIs.
This code covers the concepts in this path to BLS data.

## Key Concepts
- The top level products of the BLS are called *Surveys* each with a name and abbrevation:
    {'survey_abbreviation': 'CX', 'survey_name': 'Consumer Expenditure Survey'}   
- Access to the API uses pythons requests library, where query parameters are past to a URL
whose response is a request object with request.status_code returning succes (200) or failure (not 200).
A successful response is provided request.text property, in JSON format usually loaded as 
dictionaries and lists.
- Services within a *Survey* are called *Series*


---

"""
import pandas as pd
import requests
import json

#
# Load Surveys
#

surveys_requests = requests.get("https://api.bls.gov/publicAPI/v2/surveys")
surveys = json.loads(surveys_requests.text)
# surveys["Results"]['survey'] is a list of dictionaries
# {'survey_abbreviation': 'CX', 'survey_name': 'Consumer Expenditure Survey'}

#
# Load the key dimensions from https://download.bls.gov/pub/time.series/cx
#

# spend_items holds the hierarchy of category, subcategory and item codes 
items = pd.read_csv('https://download.bls.gov/pub/time.series/cx/cx.item',
                        sep='\t', lineterminator='\n')

subcategories = pd.read_csv('https://download.bls.gov/pub/time.series/cx/cx.subcategory',
                        sep='\t', lineterminator='\n')

spend_items = pd.merge(items[["subcategory_code", "item_code","item_text"]],
         subcategories[["category_code", "subcategory_code", "subcategory_text"]],
         on="subcategory_code", how="outer")\
         [["category_code","subcategory_code", "subcategory_text", "item_code","item_text"]]

# demo_chars shows the CE survey's characteristics grouped by demographic codes
characteristics = pd.read_csv('https://download.bls.gov/pub/time.series/cx/cx.characteristics',
                        sep='\t', lineterminator='\n')

demographics = pd.read_csv('https://download.bls.gov/pub/time.series/cx/cx.demographics',
                        sep='\t', lineterminator='\n')

demo_chars = pd.merge(demographics[["demographics_code","demographics_text"]],
         characteristics[["demographics_code","characteristics_code", "characteristics_text"]],
         on="demographics_code", how="outer")\
         [["demographics_code","demographics_text", "characteristics_code", "characteristics_text"]]

#
# Download "AllData"
#       dimensioned by series_id, year, period, value and footnote_codes
#
alldata = pd.read_csv('https://download.bls.gov/pub/time.series/cx/cx.data.1.AllData',
                        sep='\t', lineterminator='\n')
alldata = alldata.replace(' ','', regex=True)
alldata.columns = [c.replace(" ","") for c in alldata.columns.to_list()]

# series are the joint of demo_chars and spend_items
#   confirmed that alldata and series are consistent on series_id
#   note series are created and discontinued so series observed in a given year
series = pd.read_csv('https://download.bls.gov/pub/time.series/cx/cx.series',
                        sep='\t', lineterminator='\n')
series = series.replace(' ','', regex=True)
series.columns = [c.replace(" ","") for c in series.columns.to_list()]
