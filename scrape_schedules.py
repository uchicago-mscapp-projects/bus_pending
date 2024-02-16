import pandas as pd
import pathlib
import re
import requests
import zipfile

# Filenames
URL = 'https://www.transitchicago.com/downloads/sch_data/'
STOPS = 'CTA_STOP_XFERS.txt'
SCHEDULES = 'stop_times.txt'
TRIPS = 'trips.txt'
ZIP = 'google_transit.zip'
# Names for dataframes
NAMES_STOPS = ['stop_id', 'stop_code', 'stop_name', 'stop_desc', \
                'stop_lat', 'stop_lon', 'location_type', 'parent_station', \
                'wheelchair_boarding']


def download_file(url, file):
    '''
    Download stops from the CTA transit site and then save it as a local file
    in data. If it's a zip file, it unzips it into the directory

    Input:
        url (str): CTA Transit Schedule site
        file (str): File name to pul from the CTA site.

    Returns (none): Saved file in place
    '''
    request = requests.get(f'{url}{file}')
    with open(pathlib.Path(f'data/{file}'), 'wb') as f:
        f.write(request.content)

    # Unzip file if it's a zip file
    # from https://stackoverflow.com/a/36662770
    if re.match( r'.zip$', file): 
        with zipfile.ZipFile(f'data/{file}', 'r') as zip_ref:
            zip_ref.extractall('data/')

    return None
    

def load_txt_as_csv(file, names = None):
    '''
    Loads the txt file and creates a dataframe with column headers
    that align to the schema.

    Input:
        file (str): Filepath to the stops csv to import
        [Optional] names (List of strs or NOne): List of column names that are 
            not imported.

    Returns (pd.DataFrame): Data frame of the stops file to write to the 
        buses.db database.
    '''
    if names:
        rv = pd.read_csv(pathlib.Path(f'data/{file}'), names = names, header = None)
    else:
        rv = pd.read_csv(pathlib.Path(f'data/{file}'))
    return rv


def convert_df_to_json():
    '''
    '''
    pass


def write_to_db():
    '''
    '''
    pass


def scrape(url, to_download, to_clean, names = None):
    '''
    Load files from the URL, and then load remaining files into the buses.db
    file.

    Input:
        url (str): URL to download CTA schedule and files from
        to_download (List of 2 strs): Files to download from the CTA site
        to_clean (List of 3 strs): Txt files to load into pandas dataframes
            to be written to 
        names (List of Lists of strs): Lists of column names for the CTA

    Returns (None): Modifies database in place
    '''
    if len(to_clean) != len(names):
        ValueError('Length of to_clean must be the same as to_download')

    # Download files
    for file in to_download:
        download_file(url, file)

    # Load
    # TODO
