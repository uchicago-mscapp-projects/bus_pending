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
from .acs_key import ACS_KEY

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


def make_query(url_query):
    response = requests.get(query_url)
    print(response.text)