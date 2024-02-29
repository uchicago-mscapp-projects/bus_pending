import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import re
import pathlib

# filename = pathlib.Path(__file__).parent / "data/buses_calendar_added.db"
# print(filename)
filename = "/Users/danielm/Documents/UChicago/Harris/Computer_Science_2/Test_project/buses_calendar_added.db"
query_sch = """
SELECT schedule.*, trips.route_id, trips.direction, calendar.*
FROM schedule
LEFT JOIN trips ON schedule.trip_id = trips.trip_id
LEFT JOIN calendar ON trips.service_id = calendar.service_id
ORDER BY schedule.arrival_time;
"""
seconds_in_day = 86400


def analyze_schedule(filename, query_sch):
    df_schedule = query_schedule(filename, query_sch)
    # Convert multiple boolean variables into one. Also duplicates a row, but the label will be different(monday, tuesday, etc)
    melted_df = pd.melt(
        df_schedule,
        id_vars=["trip_id", "arrival_time", "stop_id", "direction", "route_id"],
        value_vars=[
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ],
        var_name="day",
        value_name="runs",
    )
    # Keep only observations where the service_id is run in that day
    filtered_df = melted_df[melted_df["runs"] == 1]
    transformed_df = keep_last_and_first(filtered_df)
    transformed_df[["start_time", "finish_time"]] = transformed_df[
        ["start_time", "finish_time"]
    ].applymap(clean_time)
    # Create duration_trip
    transformed_df["duration_trip"] = transformed_df.apply(
        lambda row: calculate_trip_duration(row["start_time"], row["finish_time"]),
        axis=1,
    )
    transformed_df["day_time"] = transformed_df["start_time"].apply(label_time_interval)
    average_trip_duration = transformed_df.groupby(
        ["day", "direction", "route_id", "day_time"]
    )["duration_trip"].mean()

    # Now calculate the average difference of start times inside groups
    transformed_df_sorted = transformed_df.sort_values(
        by=["direction", "route_id", "day_time", "start_time"]
    )
    transformed_df_sorted["start_time_diff"] = transformed_df_sorted.groupby(
        ["day", "direction", "route_id", "day_time"]
    )["start_time"].diff()
    average_start_time_diff = transformed_df_sorted.groupby(
        ["day", "direction", "route_id", "day_time"]
    )["start_time_diff"].mean()
    return average_start_time_diff, average_trip_duration


def query_schedule(filename, query):
    # Connect to the SQLite database
    conn = sqlite3.connect(filename)
    # Fetch the data into a pandas DataFrame
    df_schedule = pd.read_sql_query(query, conn)
    conn.close()
    return df_schedule


def keep_last_and_first(filtered_df):
    """
    Dataframe has the same trip_id in multiple columns. We only want to analyze
    the time at the starting point and the time at the end of the trip. Clean
    the dataframe so it only includes the first and last observation per trip_id.
    This is possible because the query sorted the trips by arrival_time

    Inputs:
        filtered_df (dataframe): dataframe that already has the days that service
            is provided

    Return:
        transformed_df (dataframe): dataframe that only has the first and
            last observation of every trip_id
    """
    # Group by 'trip_id' and select the first and last observations
    first_last_obs = filtered_df.groupby("trip_id").agg(["first", "last"])
    # Reset index to make 'trip_id' a regular column
    first_last_obs.reset_index(inplace=True)
    # Concatenate the 'trip_id', first, and last observations. All rows, starting from col 1 step size of two
    selected_obs = pd.concat(
        [
            first_last_obs["trip_id"],
            first_last_obs.iloc[:, 1::2],
            first_last_obs.iloc[:, 2::2],
        ],
        axis=1,
    )
    transformed_df = selected_obs[
        [
            "trip_id",
            ("day", "first"),
            ("arrival_time", "first"),
            ("stop_id", "first"),
            ("direction", "first"),
            ("route_id", "first"),
            ("arrival_time", "last"),
        ]
    ]
    transformed_df.reset_index(drop=True, inplace=True)
    # Clean column names
    mapping = {
        "trip_id": "trip_id",
        ("day", "first"): "day",
        ("arrival_time", "first"): "start_time",
        ("stop_id", "first"): "stop_id",
        ("direction", "first"): "direction",
        ("route_id", "first"): "route_id",
        ("arrival_time", "last"): "finish_time",
    }
    transformed_df = transformed_df.rename(mapping, axis=1)
    return transformed_df


# Clean time data. Go from string to time
def clean_time(time_str):
    """
    Some observations registered 24 and 25 hours, we have to fix it before
    making it time object. Go from string to time
    """
    # Parse time string into a datetime object
    time_str = re.sub(r"^24", "00", time_str)
    time_str = re.sub(r"^25", "01", time_str)
    return datetime.strptime(time_str, "%H:%M:%S")


def calculate_trip_duration(start_time, finish_time):
    """
    Take column finish time and start time and estimate the duration trip.
    Return the total seconds it took. Given to data cleaning requirements, some
    observations may have negative values: we have to add the total seconds of
    one day (it happened with observations that began late in the night and
    finished the next day)

    Inputs:
        start_time (datetime): start time of the bus trip
        finish_time (datetime): finish time of the bus trip

    Return:
        duration_trip (Timedelta): trip duration
    """
    # Create duration_trip
    duration_trip = finish_time - start_time
    if duration_trip < pd.Timedelta(0):
        duration_trip += pd.Timedelta(seconds=seconds_in_day)
    return duration_trip


# # Create label time (morning, afternoon, night)
# def label_time_interval(time_obs):
#     """
#     Given different thresholds, label the time the trip started

#     Inputs:
#         time_obs: time object represented as %H:%M:%S

#     Return:
#         label (str): can be moring, afternoon or night
#     """

#     # Define time thresholds
#     morning_time = datetime.strptime("06:00:00", "%H:%M:%S").time()
#     afternoon_time = datetime.strptime("12:00:00", "%H:%M:%S").time()
#     night_time = datetime.strptime("18:00:00", "%H:%M:%S").time()
#     midnight_time = datetime.strptime("00:01:00", "%H:%M:%S").time()

#     # Check which time interval the time falls into
#     if morning_time <= time_obs.time() < afternoon_time:
#         return "morning"
#     elif afternoon_time <= time_obs.time() < night_time:
#         return "afternoon"
#     elif night_time <= time_obs.time() < midnight_time:
#         return "night"
#     else:
#         return "midnight"

# Create label time (morning, afternoon, night)
def label_time_interval(time_obs):
    """
    Given different thresholds, label the time the trip started

    Inputs:
        time_obs: time object represented as %H:%M:%S

    Return:
        label (str): can be moring, afternoon or night
    """

    # Define time thresholds
    morning_time = datetime.strptime("06:00:00", "%H:%M:%S").time()
    afternoon_time = datetime.strptime("12:00:00", "%H:%M:%S").time()
    night_time = datetime.strptime("20:00:00", "%H:%M:%S").time()
    # midnight_time = datetime.strptime("00:01:00", "%H:%M:%S").time()

    # Check which time interval the time falls into
    if morning_time <= time_obs.time() < afternoon_time:
        return "morning"
    elif afternoon_time <= time_obs.time() < night_time:
        return "afternoon"
    else:
        return "night"


average_start_time_diff, average_trip_duration = analyze_schedule(filename, query_sch)
print(average_start_time_diff["saturday"]["North"]["4"]["afternoon"])
