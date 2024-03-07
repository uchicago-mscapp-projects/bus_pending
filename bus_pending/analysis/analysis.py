import pandas as pd
import sqlite3
from datetime import datetime
import re
import pathlib


filename = pathlib.Path(__file__).parents[2] / "data/buses.db"

query_sch = """
SELECT schedule.*, trips.route_id, trips.direction, calendar.*
FROM schedule
LEFT JOIN trips ON schedule.trip_id = trips.trip_id
LEFT JOIN calendar ON trips.service_id = calendar.service_id
ORDER BY schedule.arrival_time;
"""
seconds_in_day = 86400

time_thresholds = {
    "morning_time": datetime.strptime("06:00:00", "%H:%M:%S").time(),
    "afternoon_time": datetime.strptime("12:00:00", "%H:%M:%S").time(),
    "night_time": datetime.strptime("18:00:00", "%H:%M:%S").time(),
    "midnight_time": datetime.strptime("23:59:00", "%H:%M:%S").time()
}


def analyze_schedule(filename: str, query_sch: str) -> pd.core.frame.DataFrame:
    """
    Determine if the schedule is for weekday, weekend or both. Filter data to
    keep only the first and last observation. This function will make two
    group objects to compare them with real data observations

    Inputs:
        filename (str): path of the file
        query_sch (str): query to obtain and sort the data from schedule tables

    Return:
        avg_trip_weekend (GroupBy): average trip duration on weekends. Grouped by
            route and time_day (ie morning, afternoon, night and midnight)
        avg_trip_weekday (GroupBy)
    """
    df_schedule = query_schedule(filename, query_sch)
    # If service_id has schedules on saturday or sunday, weekend equal True
    df_schedule["weekday"] = df_schedule[
        ["monday", "tuesday", "wednesday", "thursday", "friday"]
    ].any(axis=1)
    df_schedule["weekend"] = df_schedule[["saturday", "sunday"]].any(axis=1)

    transformed_df = keep_last_and_first(df_schedule)
    transformed_df[["start_time", "finish_time"]] = transformed_df[
        ["start_time", "finish_time"]
    ].applymap(clean_time)
    # Create duration_trip
    transformed_df["duration_trip"] = transformed_df.apply(
        lambda row: calculate_trip_duration(row["start_time"], row["finish_time"]),
        axis=1,
    )
    transformed_df["day_time"] = transformed_df["start_time"].apply(label_time_interval)
    avg_trip_weekday = transformed_df.groupby(["weekday", "route_id", "day_time"])[
        "duration_trip"
    ].mean()
    avg_trip_weekend = transformed_df.groupby(["weekend", "route_id", "day_time"])[
        "duration_trip"
    ].mean()
    return avg_trip_weekend, avg_trip_weekday


def query_schedule(filename: str, query: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(filename)
    # Fetch the data into a pandas DataFrame
    df_schedule = pd.read_sql_query(query, conn)
    conn.close()
    return df_schedule


def keep_last_and_first(filtered_df: pd.core.frame.DataFrame):
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
    transformed_df = clean_columns(selected_obs)
    return transformed_df


def clean_columns(df_colapsed: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """
    After collapsing the dataframe to have only the first and the last observation
    per trip, keep only columns of interest and clean column names

    Inputs:
        df_colapsed (dataframe): dataframe after collapsing to keep desired observations

    Return:
        transformed_df (dataframe): cleaned dataframe
    """
    transformed_df = df_colapsed[
        [
            "trip_id",
            ("weekday", "first"),
            ("weekend", "first"),
            ("arrival_time", "first"),
            ("stop_id", "first"),
            ("route_id", "first"),
            ("arrival_time", "last"),
        ]
    ]
    transformed_df.reset_index(drop=True, inplace=True)
    # Clean column names
    mapping = {
        "trip_id": "trip_id",
        ("weekday", "first"): "weekday",
        ("weekend", "first"): "weekend",
        ("arrival_time", "first"): "start_time",
        ("stop_id", "first"): "stop_id",
        ("route_id", "first"): "route_id",
        ("arrival_time", "last"): "finish_time",
    }
    transformed_df = transformed_df.rename(mapping, axis=1)
    return transformed_df


def clean_time(time_str: str) -> datetime:
    """
    Some observations registered 24 and 25 hours, we have to fix it before
    making it time object. Go from string to time
    """
    # Parse time string into a datetime object
    time_str = re.sub(r"^24", "00", time_str)
    time_str = re.sub(r"^25", "01", time_str)
    return datetime.strptime(time_str, "%H:%M:%S")


def calculate_trip_duration(start_time: datetime, finish_time: datetime) -> float:
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
        duration_trip (float): trip duration in minutes
    """
    # Create duration_trip
    duration_trip = finish_time - start_time
    if duration_trip < pd.Timedelta(0):
        duration_trip += pd.Timedelta(seconds=seconds_in_day)
    total_minutes = duration_trip.total_seconds() / 60
    return total_minutes


def label_time_interval(time_obs: str) -> str:
    """
    Given different thresholds, label the time the trip started

    Inputs:
        time_obs (str): time object represented as %H:%M:%S

    Return:
        label (str): can be moring, afternoon or night
    """

    # Define time thresholds
    morning_time = time_thresholds["morning_time"]
    afternoon_time = time_thresholds["afternoon_time"]
    night_time = time_thresholds["night_time"]
    midnight_time = time_thresholds["midnight_time"]

    # Check which time interval the time falls into
    if morning_time <= time_obs.time() < afternoon_time:
        return "morning"
    elif afternoon_time <= time_obs.time() < night_time:
        return "afternoon"
    elif night_time <= time_obs.time() < midnight_time:
        return "night"
    else:
        return "midnight"
