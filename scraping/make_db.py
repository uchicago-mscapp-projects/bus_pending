import json
import pathlib
import sqlite3

SCHEMA_BUSES = '''
    CREATE TABLE buses (
        vid INTEGER PRIMARY KEY,
        tmstmp TEXT,
        lat REAL, 
        lon REAL,
        hdg INTEGER,
        pid INT,
        pdist INT,
        rt TEXT,
        des TEXT,
        dly BOOLEAN,
        tatripid INTEGER,
        tablockid TEXT,
        zone TEXT,
        origtatripno INTEGER,
       );
'''
# TODO: Add FOREIGN_KEYS
# TODO: Add indexing

SCHEMA_TIMES = '''
'''

def make_db():
    '''
    Create database from saved schema
    '''

    # First generate path
    path = pathlib.Path("data/bus.db")

    # Create a new connection to a path
    connection = sqlite3.connect(path)
    cursor = connection. cursor()

    # Create table for both schems
    for schema in [SCHEMA_BUSES, SCHEMA_TIMES]:
        cursor.execute(schema)


# Create database if called from the command line 
if __name__ == "__main__":
    make_db()
