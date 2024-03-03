import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import re

final_dfs = pd.read_csv("/Users/danielm/Downloads/trip_level.csv")
final_dfs = final_dfs[final_dfs['consecutive_counts_y'].notna()]

def do_analysis(final_dfs):
    final_dfs['ghost'] = final_dfs.apply(lambda x: find_ghost_buses(x, mean_dist_route, std_distance_route), axis=1)
    desired_columns = ['rt', 'day_time', 'weekend', 'ghost', 'consecutive_counts_y']
    final_dfs = final_dfs[desired_columns]
    return final_dfs

def determine_time_data(time_stmp):
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

final_dfs[['day_time', 'weekend']] = final_dfs['tmstmp'].apply(lambda x: pd.Series(determine_time_data(x)))

mean_dist_route = final_dfs.groupby("rt")["total_dist"].mean()
std_distance_route = final_dfs.groupby("rt")["total_dist"].std()

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
    route = observation['rt']
    total_distance = observation["total_dist"]
    mean_distance = mean_dist_route.get(route, np.nan)
    
    if np.isnan(mean_distance):
        return False
    std_distance = std_distance_route.get(route, np.nan)
    if np.isnan(std_distance):
        return False
    
    if (total_distance > mean_distance + 2* std_distance) or (total_distance < mean_distance - 2 * std_distance):
        return True
    else:
        return False
    

final_dfs['ghost'] = final_dfs.apply(lambda x: find_ghost_buses(x, mean_dist_route, std_distance_route), axis=1)
desired_columns = ['rt', 'day_time', 'weekend', 'ghost', 'consecutive_counts_y']
final_dfs = final_dfs[desired_columns]
    
