import json
import pathlib
import sqlite3

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
        tatripid INTEGER,
        tablockid TEXT,
        zone TEXT,
        origtatripno INTEGER,
        PRIMARY KEY (vid, tmstmp),
        FOREIGN KEY (rt) REFERENCES schedule(rt)
    );
'''

SCHEMA_STOPS = '''
    CREATE TABLE stops (
        stop_id INT NOT NULL,
        stop_code INT NOT NULL,
        stop_name TEXT NOT NULL,
        stop_desc TEXT,
        stop_lat REAL NOT NULL,
        stop_lon REAL NOT NULL,
        location_type BOOLEAN,
        parent_station BOOLEAN,
        wheelchair_boarding BOOLEAN,
        PRIMARY KEY (stop_desc)
    );
'''

# From stop_times
SCHEMA_SCHEDULE = '''
    CREATE TABLE schedule (
        trip_id TEXT NOT NULL, 
        arrival_time TEXT NOT NULL, 
        departure_time TEXT NOT NULL,
        stop_id INT NOT NULL, 
        stop_sequence INT, # Order of routes 
        stop_headsign TEXT NOT NULL, # End stattion
        pickup_type BOOL,
        shape_dist_traveled TEXT,
        PRIMARY KEY (trip_id, stop_id, stop_headsign),
        FOREIGN KEY (stop_id) REFERENCES stops(stop_desc)
    );
'''


def make_db():
    '''
    Create database from saved schema
    '''
    # First generate path
    path = pathlib.Path("data/buses.db")

    # Create a new connection to a path
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    # Create table for both schems
    for schema in [SCHEMA_BUSES, SCHEMA_SCHEDULE, SCHEMA_STOPS]:
        cursor.execute(schema)
    cursor.close()
