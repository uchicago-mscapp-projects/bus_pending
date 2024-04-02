import pandas as pd
import numpy as np
from datetime import datetime
from bus_pending.analysis.analysis import analyze_schedule, filename, query_sch
from typing import Tuple
import pathlib


def determine_time_data(time_stmp: str) -> Tuple[str, bool]:
    """
    Given a time stamp, determine if the observation was on weekend and the
    time of the day (morning, afternoon, night or midnight)

    Inputs:
        time_stamp (str): time stamp with the format %Y%m%d %H:%M

    Return:
        day_time (str): time of the day (morning, night, etc)
        weekend (bool): True if it was a weekend and False otherwise
    """
    date_object = datetime.strptime(time_stmp, "%Y%m%d %H:%M")
    day = date_object.weekday()
    weekend = None
    
    if day < 5:
        weekend = True
    else:
        weekend = False

    day_time = None
    # Thresholds
    morning_time = datetime.strptime("06:00:00", "%H:%M:%S").time()
    afternoon_time = datetime.strptime("12:00:00", "%H:%M:%S").time()
    night_time = datetime.strptime("18:00:00", "%H:%M:%S").time()
    midnight_time = datetime.strptime("23:59:00", "%H:%M:%S").time()

    time_obs = date_object.time()
    if morning_time <= time_obs < afternoon_time:
        day_time = "morning"
    elif afternoon_time <= time_obs < night_time:
        day_time = "afternoon"
    elif night_time <= time_obs < midnight_time:
        day_time = "night"
    else:
        day_time = "midnight"
    return day_time, weekend


def find_ghost_buses(observation, mean_dist_route, std_distance_route):
    """
    Given an observation, compare the ditance it should have travelled in average
    considering the route. If it is two standard deviations from the mean label
    it as ghost bus

    Inputs:
        observation (row): row from a data frame
        mean_dist_route (group object): object grouped by route_id that has the
        average total distance

    Return:
        boolean (bool): True if ghost bus False otherwise
    """
    route = observation["rt"]
    total_distance = observation["total_dist"]
    mean_distance = mean_dist_route.get(route, np.nan)

    if np.isnan(mean_distance):
        return False
    std_distance = std_distance_route.get(route, np.nan)
    if np.isnan(std_distance):
        return False

    if (total_distance > mean_distance + 2 * std_distance) or (
        total_distance < mean_distance - 2 * std_distance
    ):
        return True
    else:
        return False


def create_df_stats(final_dfs: pd.core.frame.DataFrame) -> pd.core.frame.DataFrame:
    """
    Given the dataframe, create a new dataframe with basic stats by route.
    Add columns for n delayed buses, percentage delayed, total trips and
    max delay time by route

    Inputs:
        final_dfs (DataFrame): DataFrame with all the desired data. User can
            explore this further if he/she wants to derive different stats

    Return:
        delayed_df_with_max_delay (DataFrame): DataFrame with basic stats by
            route
    """
    final_dfs_filtered = final_dfs[final_dfs["delayed_time"] != 20]
    # Group by 'rt' and calculate the total number of trips for each group
    total_trips_rt = final_dfs_filtered.groupby("rt").size()
    # Group by 'rt' and calculate the sum of delays for each group
    n_delayed_rt = final_dfs_filtered.groupby("rt")["delay"].sum()
    percentage_delayed_rt = (n_delayed_rt / total_trips_rt) * 100

    # Create a new DataFrame with 'rt', 'n_delayed', 'percentage_delayed', and 'total_trips' columns
    delayed_df = pd.DataFrame(
        {
            "rt": total_trips_rt.index,
            "n_delayed": n_delayed_rt.values,
            "percentage_delayed": percentage_delayed_rt.values,
            "total_trips": total_trips_rt.values,
        }
    )

    delayed_df_sorted = delayed_df.sort_values(by="percentage_delayed", ascending=False)
    max_delayed_time_rt = final_dfs_filtered.groupby("rt")["delayed_time"].max()

    # Create a new DataFrame with 'rt' and 'max_delayed_time' columns
    max_delayed_time_df = pd.DataFrame(
        {
            "rt": max_delayed_time_rt.index,
            "max_delayed_time": max_delayed_time_rt.values,
        }
    )
    # Merge with existing DataFrame
    delayed_df_with_max_delay = delayed_df_sorted.merge(max_delayed_time_df, on="rt")
    return delayed_df_with_max_delay


def estimate_delay(
    df_real_data: pd.core.frame.DataFrame, avg_trip_weekday, avg_trip_weekend
):
    """
    Calculate delay time based on schedule time averages by route, day_time
        and initial split of weekdays and weekends. This will make changes
        in place

    Input:
        df_real_data (DataFrame): DataFrame we want to analyze
    """
    for _, observation in df_real_data.iterrows():
        if observation["weekend"]:
            group = avg_trip_weekend
        else:
            group = avg_trip_weekday
        route = observation["rt"]
        day_time = observation["day_time"]
        if observation["ghost"]:
            df_real_data.loc[observation.name, "delayed_time"] = 20
            continue
        expected_time = group.get((True, route, day_time), np.nan)
        if np.isnan(expected_time):
            # Drop the row if we did not have observations in schedule data
            df_real_data.drop(index=observation.name, inplace=True)
            continue
        delayed_time = observation["consecutive_counts_y"] - expected_time
        if delayed_time > 10:
            df_real_data.loc[observation.name, "delayed_time"] = delayed_time
        else:
            df_real_data.loc[observation.name, "delayed_time"] = 0


def do_analysis():
    """
    This function does all the analysis. From analyzing schedule data to analyze
        real data and then compare them to estimate delays. Creates two
        different csv files with information aboute routes. First file contains
        all data by route so the user can derive new stats. Second file contains
        basic stats by route

    Input:
        final_dfs (DataFrame): dataframe cleaned in cleaning directory
    """
    final_dfs = pd.read_csv(pathlib.Path(__file__).parents[2] / "data/trip_time_level.csv")
    final_dfs = final_dfs[final_dfs["consecutive_counts_y"].notna()]
    csv_path_stats = pathlib.Path(__file__).parents[2] / "data/stats_df.csv"
    csv_path_complete = pathlib.Path(__file__).parents[2] / "data/complete_info.csv"
    avg_trip_weekday, avg_trip_weekend = analyze_schedule(filename, query_sch)

    final_dfs[["day_time", "weekend"]] = final_dfs["tmstmp"].apply(
        lambda x: pd.Series(determine_time_data(x))
    )
    mean_dist_route = final_dfs.groupby("rt")["total_dist"].mean()
    std_distance_route = final_dfs.groupby("rt")["total_dist"].std()
    final_dfs["ghost"] = final_dfs.apply(
        lambda x: find_ghost_buses(x, mean_dist_route, std_distance_route), axis=1
    )
    desired_columns = ["rt", "day_time", "weekend", "ghost", "consecutive_counts_y"]
    final_dfs = final_dfs[desired_columns]
    estimate_delay(final_dfs, avg_trip_weekday, avg_trip_weekend)
    final_dfs["delay"] = final_dfs["delayed_time"].apply(lambda x: 1 if x > 0 else 0)
    final_dfs.to_csv(csv_path_complete)
    df_stats = create_df_stats(final_dfs)
    df_stats.to_csv(csv_path_stats)
    