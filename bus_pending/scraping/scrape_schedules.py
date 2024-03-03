import pandas as pd
import pathlib
import re
import requests
import zipfile

from scraping.make_db import save_request
from typing import List


# Filenames
URL = 'https://www.transitchicago.com/downloads/sch_data/'
CALENDAR = 'calendar.txt'
SCHEDULE = 'stop_times.txt'
STOPS = 'stops.txt'
TRIPS = 'trips.txt'
ZIP = 'google_transit.zip'
# Names for dataframes
STOPS_KEYS = ['stop_id', 'stop_code', 'stop_name', 'stop_desc', 'stop_lat', \
              'stop_lon', 'location_type', 'parent_station', \
              'wheelchair_boarding']
SCHEDULE_KEYS = ['trip_id', 'arrival_time', 'departure_time', 'stop_id', \
                 'stop_sequence', 'stop_headsign', 'pickup_type', \
                 'shape_dist_traveled']
TRIPS_KEYS = ['route_id','service_id', 'trip_id', 'direction_id', 'block_id', \
              'shape_id','direction', 'wheelchair_accessible', 'schd_trip_id']
CALENDAR_KEYS = ['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 
                 'friday', 'saturday', 'sunday', 'start_date', 'end_date']
# List of tuples for scraping scripts
TO_CLEAN = [(STOPS, STOPS_KEYS, 'stops'), \
            (SCHEDULE, SCHEDULE_KEYS, 'schedule'), \
            (TRIPS, TRIPS_KEYS, 'trips'), \
            (CALENDAR, CALENDAR_KEYS, 'calendar')]


def download_file(url: str, file: str) -> None:
    '''
    Download stops from the CTA transit site and then save it as a local file
    in data. If it's a zip file, it unzips it into the directory

    Input:
        url (str): CTA Transit Schedule site
        file (str): File name to pul from the CTA site.

    Returns (none): Saved file in place
    '''
    request = requests.get(f'{url}{file}')
    data_path = pathlib.Path(__file__).parents[2] / 'data/' 
    with open(f'{data_path}/{file}', 'wb') as f:
        f.write(request.content)

    # Unzip file
    # from https://stackoverflow.com/a/36662770
    with zipfile.ZipFile(f'{data_path}/{file}', 'r') as zip_ref:
        zip_ref.extractall('data/')

    return None
    

def load_txt_as_csv(file: str) -> List[dict]:
    '''
    Loads the txt file and creates a dataframe with column headers
    that align to the schema.

    Input:
        file (str): Filepath to the stops csv to import

    Returns (list of dicts): List of dataframe elements to write into DB
    '''
    data_path = pathlib.Path(__file__).parents[2] / 'data/' 
    df = pd.read_csv(f'{data_path}/{file}')
    return df.to_dict('records')


def scrape() -> None:
    '''
    Load files from the URL, and then load remaining files into the buses.db
    file.

    Input (None): None, all hardcoded

    Returns (None): Modifies database in place
    '''
    # Download files
    download_file(URL, ZIP)
    db_path = pathlib.Path(__file__).parents[2] / 'data/buses.db'

    # Load
    for file, names, table in TO_CLEAN:
        print(f'Creating schedule database elements: {table}')
        lst = load_txt_as_csv(file)

        # Save them to the buses.db database
        save_request(lst, db_path, f'{table}', names) 
