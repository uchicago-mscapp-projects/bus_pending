import requests
import math
import json
import time
import pathlib

# TODO Hardcoded parameters
ROUTES = ["1", "2", "3", "4", "X4", "5" ,"6" ,"7" , "8", "8A", "9"]

def get_api_key(file):
    '''
    Function to load an API key from a file

    Input:
        file (str): File with API stored as plain text. This file is expected
            to be in a file called .apikey which is hidden by the .gitignore
            file.
    
    Returns: (str) API Key
    '''
    try:
        with open(file) as f:
            key = f.read()
            return key.strip()
    except FileNotFoundError:
        print(f'Did not locate {file}')


def make_bus_request(key, routes, format):
    '''
    Makes a request to the CTA bus tracker API with the following parameters.

    Args:
        key (str):
        routes (str):
        format (str):

    Returns (list): A list of JSON responses from the query
    '''
    url = "http://ctabustracker.com/bustime/api/"
    version = "v2/"
    request = "getvehicles?"
    if format not in ["json", "xml"]:
        ValueError("The CTA Bustracker API only allows JSON or XML outputs")

    # For each route list loop through them in units of ten, the max of API
    rv = []
    for i in range(math.ceil(len(routes)/10)):
                
        # Set-up query parameters 
        chunk = routes[i * 10:(i + 1) * 10]
        rt = ','.join(chunk)

        # Query API
        print(f'Calling routes - {i + 1}')
        pos_chunk = requests.get(f'{url}{version}{request}key={key}&rt={rt}&format={format}')
        time.sleep(1) # One second between route things
    
        # TODO Validate query
        # Response from server
        # Data exists
            
        rv.append(pos_chunk.json())

    return rv


def save_request(request, location):
    '''
    Saves a request output as a JSON to the specified location.

    Input:
        request (lst): A dictionary storing the JSON elements.
        location (str): A file path to store the elements

    Returns: None. Saves the list of request to the file.
    '''
    # TODO: Add adding to the location

    # Save data to JSON
    with open(f'{location}.json', 'w') as f:
        json.dump(request, f, indent = 1)


def scrape_bus_api(file):
    '''
    Wrapper function to use an API key and then call the

    Inputs:
        file (str): Filepath and name of the output file to create from the
            scraper.
    
    Return (None): Saves output file
    '''
    # Get key from file
    key = get_api_key('.apikey')

    # Establish routes
    routes = ROUTES # Hardcoded

    positions = make_bus_request(key, routes, 'json')
    save_request(positions, f"{file}")


def create_test_data(num, file):
    '''
    Run multiple iterations of the scraper.

    Note: TEST version includes a section save the file over and over
        again.

    Input:
        num (int): How many times to iterate through the scraper.
    '''
    # New name
    temp_name = file + "_temp"
    for _ in range(num):
        scrape_bus_api(temp_name)

        # Load saved JSON
        with open(f'{temp_name}.json') as f:
            iter = json.load(f)
        
        # Load full JSON
        pos_json = pathlib.Path("pos.json")
        if pos_json.exists():
            with open(f'{file}.json') as f:
                temp = json.load(f)
            combined = temp + iter # TODO Figure out why string concat works
        else:
            combined = iter.copy()
        
        # Save open JSON
        with open(f'{file}.json', "w") as f:
            json.dump(combined, f, indent = 1)
        
        time.sleep(60 - math.ceil(len(ROUTES)/10)) # 2 1 sec sleeps above, so keep on time


# TODO: Command line implementation
