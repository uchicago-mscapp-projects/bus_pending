import pandas as pd
import numpy as np
from datetime import datetime
from bus_pending.analysis.analysis import time_thresholds
from typing import Tuple


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
    morning_time = time_thresholds["morning_time"]
    afternoon_time = time_thresholds["afternoon_time"]
    night_time = time_thresholds["night_time"]
    midnight_time = time_thresholds["midnight_time"]

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
    delayed_df_with_max_delay = merge_max_delayes_df(final_dfs_filtered, delayed_df_sorted)
    return delayed_df_with_max_delay


def merge_max_delayes_df(final_dfs_filtered, delayed_df_sorted):
    """
    Estimate the maximum delay time per route and merge the result with our
    stats dataframe

    Inputs:
        final_dfs_filtered (dataframe): dataframe with all the information
        delayed_df_sorted (dataframe): has already the other stats per route

    Return:
        delayed_df_with_max_delay(dataframe): new dataframe that now has the
            variable max_delayed_time per route
    """
    max_delayed_time_rt = final_dfs_filtered.groupby("rt")["delayed_time"].max()
    max_delayed_time_df = pd.DataFrame(
        {
            "rt": max_delayed_time_rt.index,
            "max_delayed_time": max_delayed_time_rt.values,
        }
    )
    # Merge with existing DataFrame with stats
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
    

def label_ghosts(final_dfs):
    """
    As we defined in the README, we are going to consider two standard deviations
    from the average distance in x route to label a bus as a ghost. If it
    traveled considerable less distance then it didnt complete the trip. We need
    to estimate the mean and sd per route

    Inputs:
        final_dfs (dataframe): dataframe with day_time and weekend variables
    
    Return:
        df_ghosts (dataframe): dataframe with boolean variable ghost that
            indicates a bus didnt complete the route. Also it only has the
            desired columns
    """
    mean_dist_route = final_dfs.groupby("rt")["total_dist"].mean()
    std_distance_route = final_dfs.groupby("rt")["total_dist"].std()
    final_dfs["ghost"] = final_dfs.apply(
        lambda x: find_ghost_buses(x, mean_dist_route, std_distance_route), axis=1
    )
    desired_columns = ["rt", "day_time", "weekend", "ghost", "consecutive_counts_y"]
    df_ghosts = final_dfs[desired_columns]
    return df_ghosts
