import json
import math
import pathlib
import time

from scraping.scrape_buses import scrape_bus_api


def create_routes():
    '''
    Scrape routes and return a routes variable for test data.

    Input (None)

    Returns
        routes (list): List of routes to scrape.
    '''
    with open('routes.txt') as f:
        data = f.read()
    return data.split(',')


def create_test_data(num, file):
    '''
    Run multiple iterations of the scraper.

    Note: TEST version includes a section save the file over and over
        again.

    Input:
        num (int): How many times to iterate through the scraper.
    '''
    # Get routes:
    routes = create_routes()

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
        
        time.sleep(60 - math.ceil(len(routes)/10) -2) # N 1 sec sleeps above, plus 2 seconds to run 13
