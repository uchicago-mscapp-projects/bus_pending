import requests

from scraping.scrape_buses import get_stored_data

def get_routes(file = "routes.txt"):
    '''
    Queries if the CTA bustracker API and saves a local version of the routes 
    file.

    Input:
        key(txt): API key to use from the

    Return (None): Saves a .txt file as a comma-delimited string with the 
        string in the main directory.
    '''
    # Get key
    key = get_stored_data(".apikey", 'key')

    # Store API elements
    url = "http://ctabustracker.com/bustime/api/"
    ver = "v2/"
    req = "getroutes"

    # Make request as a JSON
    rts = requests.get(f"{url}{ver}{req}?key={key}&format=json")

    # Print message if key error 
    if rts.json()['bustime-response']['error']:
        raise ValueError(f"Received error: {rts.json()['bustime-response']['error']['msg']}")
    
    # Extract response as a list and then store as a list
    rv = []
    data = rts.json()['bustime-response']
    for rt in data['routes']:
        rv.append(rt['rt'])

    # Save file 
    with open(file, "w") as f:
        f.write(",".join(rv))
