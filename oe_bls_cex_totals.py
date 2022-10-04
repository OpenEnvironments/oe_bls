import pandas as pd
import numpy as np

def oe_bls_cex_totals(year):
    """
    This function downloads the CEX summary report for a given year,
    then interprets to return the mean values for each reported Item.
    The BLS spreadsheet includes footnote marks, appended text and
    number formatting so this function is a set of cleanup rules.

    :param  year:      a string of the requested year   "2018", eg
    :return usmeans:   a dataframe with the mean values for each Item
    
    """

    ustotal = pd.read_excel(("https://www.bls.gov/cex/tables/calendar-year/mean/cu-all-detail-"+year+".xlsx"), 
                            skiprows=2,dtype=object)

    ustotal.columns = [c.replace('\n',' ').replace('- ','-') for c in ustotal.columns]

    replacedict = {'a/ ': '','b/ ':'', ':': '','n.a.':'',
                    ' []':'',' [D]':'',' [I]':'',
                   '\$': '', ',': '','a/ ':'','b/ ':''}

    for r in replacedict.keys():
        ustotal["Item"] = ustotal["Item"].str.replace(r,replacedict[r],regex=False)

    usdict = {}
    for i,r in ustotal.iterrows():
        # The total row labels its own value
        # but all other Items have a label followed by 3 addl rows for "Mean","Variance","%"
        # Look for any rows with Item "Mean" and generate a row with the prev Item label
        if "Number of consumer units (in thousands)" in str(r[0]):
            usdict["Number of consumer units (in thousands)"] = r[1]
        if r.Item == "Mean":
            usdict[lastitem]=r[1]
        lastitem = r.Item

    ussum = pd.DataFrame.from_dict({"Item":usdict.keys(),"Amount":usdict.values()})
    ussum["Amount"] = ussum.Amount.fillna(np.nan).apply(lambda x: pd.to_numeric(x, errors='coerce'))
    
    return ussum