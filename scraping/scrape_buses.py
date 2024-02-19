import requests
import math
import time

from scraping.make_db import save_request

BUS_KEYS = ['vid', 'tmstmp', 'lat', 'lon', 'hdg', 'pid', 'rt', 'des', \
            'pdist', 'dly', 'tatripid', 'origtatripno', 'tablockid', 'zone']

def get_stored_data(file, type):
    '''
    Function to load an API key from a file

    Input:
        file (str): File to extract from plain text.
        type (str): Type of file to extract. Two allowable options:
            key: API stored as plain text. This file is expected
                to be in a file called .apikey which is hidden by the 
                .gitignore file.
            routes: List of routes stored as a comma-delimited string on a 
                single line. Produced by the scrape_routes.py file. In the
                repo by default.
    
    Returns: (str) API Key
    '''
    try:
        with open(file) as f:
            data = f.read()
            if type == "key":
                return data.strip()
            elif type == "routes":
                return data.split(',')
            else:
                KeyError('Only "key" or "routes" are allowed data to call')
    except FileNotFoundError:
        print(f'Did not locate {file}')


def make_bus_request(key, routes):
    '''
    Makes a request to the CTA bus tracker API with the following parameters.

    Args:
        key (str): API key for the CTA bus tracker API.
        routes (str): A list of CTA bus routes to query the API from. This
            will be chunked into API requests of no more than 10 items so that
            the API will respond.

    Returns (list): A list of JSON responses from the query
    '''
    url = "http://ctabustracker.com/bustime/api/"
    ver = "v2/"
    req = "getvehicles"

    # For each route list loop through them in units of ten, the max of API
    print(f"Begin call - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print('  Calling routes:', end = " ") 
    rv = []
    for i in range(math.ceil(len(routes)/10)):
                
        # Set-up query parameters 
        chunk = routes[i * 10:(i + 1) * 10]
        rt = ','.join(chunk)

        # Query API
        print(f'{chunk[0]}-{chunk[-1]}', end = ", ", flush = True)
        pos_chunk = requests.get(f'{url}{ver}{req}?key={key}&rt={rt}&format=json')
        time.sleep(1) # One second between route chunk
    
        # Print message if key error 
        if 'error' in pos_chunk.json()['bustime-response'].keys():
            for error in pos_chunk.json()['bustime-response']['error']:
                # Exclude route not running error
                if error['msg'] != 'No data found for parameter':
                    raise ValueError(f"Received error: {pos_chunk.json()['bustime-response']['error']}")
        
        # SKip if all routes in a chunk are not running
        if 'vehicle' not in pos_chunk.json()['bustime-response'].keys():
            continue
        else:
            rv.extend(pos_chunk.json()['bustime-response']['vehicle']) # Returned under header, so index in
    
    print(f"\nEnd call - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    return rv


def scrape_bus_api(file):
    '''
    Wrapper function to use an API key and then call the

    Inputs:
        file (str): Filepath and name of the output file to create from the
            scraper.
    
    Return (None): Saves output file
    '''
    # Get key from file
    key = get_stored_data('.apikey', 'key')
    routes = get_stored_data('routes.txt', 'routes')

    # Scrape API
    positions = make_bus_request(key, routes)
    save_request(positions, f'{file}', 'buses', BUS_KEYS)
