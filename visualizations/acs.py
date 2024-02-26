"""
Code for cleaning the American Community Survey Data via API

Survey: 
American Community Suvey 1-Year Data (2005-2022)

Documentation:
https://www.census.gov/programs-surveys/acs/data/data-via-api.html
https://www.census.gov/data/developers/data-sets/acs-1year.html

Got help from: 
https://medium.com/@mcmanus_data_works/using-the-u-s-census-bureau-api-with-python-5c30ad34dbd7
"""

import requests
# from .acs_key import ACS_KEY
import pandas as pd
import numpy as np
from skimpy import clean_columns

def make_acs_request(year = 2022, variables = ["Name", "B19113_001E"], geography_code = [], api_key = ""): 
    """
    Build url to make ACS request from the API. 
    """
    
    # Declare API key from package
    if ACS_KEY: 
        api_key = ACS_KEY


    # Define url parameters    
    host = "https://api.census.gov/data/"
    table = "acs/acs1"
    get  = "get="
    vars = ",".join(variables)
    geo  = "&for=" + geography_code
    key  = "&key=" + api_key
    
    # Paste in a single query url
    url_query = host + table + year + get + vars + geo + key 

    return url_query



def clean_income_data(file, year): 
    # Open file 
    file = open(file + str(year) + ".csv")
    df_income_raw = pd.read_csv(file)
    file.close()

    # Clean data set
    # Clean variable names from income table
    df_income_wide = clean_columns(df_income_raw)
    df_income_wide = df_income_wide.drop(
        df_income_wide.filter(regex = "margin_").columns, axis = 1)

    # Select total population 
    df_income_wide = df_income_wide[df_income_wide["label_grouping"].str.contains("Total")]

    # Change to long format 
    # Store all column names for zip codes
    zip_cols = df_income_wide.columns[1:1399]
    df_income = pd.melt(df_income_wide, 
                        id_vars = "label_grouping", 
                        value_vars=zip_cols)

    df_income = df_income.rename(columns = {"variable": "zip", "value": "income"})
    df_income = df_income.drop("label_grouping", axis = 1)

    df_income["zip"] = df_income["zip"].str.replace(r"zcta_5_", "")
    df_income["zip"] = df_income["zip"].str.replace(r"_estimate", "")
    df_income["income"] = df_income["income"].str.replace(r",", "")
    df_income["income"] = df_income["income"].str.replace(r"-", "")

    # Replace observations that are entirely white space with NaN
    # Source: https://stackoverflow.com/questions/13445241/replacing-blank-values-white-space-with-nan-in-pandas
    df_income["income"] = df_income["income"].replace(r"^\s*$", np.nan, regex=True).astype(float)
    df_income["year"] = year
    
    return df_income


def write_income_series(min_year = 2018, max_year = 2022): 
    df_income_zip_code_series = pd.DataFrame()

    for year in range(min_year, max_year + 1):
        path = "acs_data/acs_income_zipcodes_"
        df_year = clean_income_data(path, year)
        
        df_income_zip_code_series = pd.concat(
            [df_income_zip_code_series, df_year])
        
    df_income_zip_code_series.to_csv("acs_data/df_income_zip_code_series.csv", 
                                     index = False)


        






