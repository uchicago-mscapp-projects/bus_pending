import pathlib
import sqlite3


# From getlocations API
SCHEMA_BUSES = '''
    CREATE TABLE buses (
        vid INTEGER NOT NULL,
        tmstmp TEXT NOT NULL,
        lat REAL NOT NULL, 
        lon REAL NOT NULL,
        hdg INTEGER NOT NULL,
        pid INT,
        pdist INT,
        rt TEXT NOT NULL,
        des TEXT NOT NULL,
        dly BOOLEAN,
        tatripid INTEGER NOT NULL,
        tablockid TEXT,
        zone TEXT,
        origtatripno INTEGER,
        PRIMARY KEY (vid, tmstmp),
        FOREIGN KEY (tatripid) REFERENCES trips(trip_id)
    );
'''

# From stops.txt
SCHEMA_STOPS = '''
    CREATE TABLE stops (
        stop_id INT NOT NULL,
        stop_code INT NOT NULL,
        stop_name TEXT NOT NULL,
        stop_desc TEXT NOT NULL,
        stop_lat REAL NOT NULL,
        stop_lon REAL NOT NULL,
        location_type BOOLEAN,
        parent_station BOOLEAN,
        wheelchair_boarding BOOLEAN,
        PRIMARY KEY (stop_desc)
    );
'''

# From stop_times.txt
SCHEMA_SCHEDULE = '''
    CREATE TABLE schedule (
        trip_id TEXT NOT NULL, 
        arrival_time TEXT NOT NULL, 
        departure_time TEXT NOT NULL,
        stop_id INT NOT NULL, 
        stop_sequence INT,
        stop_headsign TEXT NOT NULL,
        pickup_type BOOL,
        shape_dist_traveled TEXT,
        PRIMARY KEY (trip_id, stop_id, stop_headsign),
        FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
        FOREIGN KEY (stop_id) REFERENCES stops(stop_id)
    );
'''

# From trips.txt
SCHEMA_TRIPS = '''
    CREATE TABLE trips (
        route_id TEXT NOT NULL,
        service_id TEXT,
        trip_id TEXT NOT NULL,
        direction_id TEXT NOT NULL,
        block_id TEXT NOT NULL,
        shape_id TEXT_NOT NULL,
        direction TEXT NOT NULL,
        wheelchair_accessible BOOL,
        schd_trip_id TEXT NOT NULL,
        PRIMARY KEY (trip_id)
    );
'''


def make_db():
    '''
    Create database from saved schema
    '''
    # First generate path
    path = pathlib.Path("data/buses.db")
    path.unlink() # Delete if it exists already

    # Create a new connection to a path
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    # Create table for both schems
    for schema in [SCHEMA_BUSES, SCHEMA_SCHEDULE, SCHEMA_STOPS, SCHEMA_TRIPS]:
        cursor.execute(schema)
    cursor.close()


def save_request(request, location, table, keys):
    '''
    Saves a request output into the buses database.

    Input:
        request (List): A list storing the elements of a request.
        location (str): A file path to store the elements
        table (str): Name of the table to write into
        keys (List of strs): List of dict kesy from the DataFrame to write

    Returns: None. Saves the list of request to the file.
    '''
    # Create a new connection to a path
    path = pathlib.Path(f'{location}')
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    # Build parameter lists
    params = []
    for key in request[0].keys():
        params.append(f':{key}')
    # Create query to write buses
    # executemany with dict placeholders from https://stackoverflow.com/a/70548130
    query = f"INSERT OR IGNORE INTO {table} ({', '.join(keys)}) VALUES ({', '.join(params)})"

    # Write file
    cursor.executemany(query, request)
    connection.commit()
    
    # Close connection after write is completed
    connection.close()
