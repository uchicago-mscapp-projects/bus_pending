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
        PRIMARY KEY (vid, tmstmp)
       );
'''
# TODO: Add Scheduling table
# TODO: Add FOREIGN_KEYS
# TODO: Add indexing

SCHEMA_TIMES = '''
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
    for schema in [SCHEMA_BUSES]:
        cursor.execute(schema)
    cursor.close()
