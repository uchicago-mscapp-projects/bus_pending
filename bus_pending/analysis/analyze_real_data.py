import pandas as pd
import numpy as np
from analysis import averga_trip_duration
from datetime import datetime
import re

final_dfs = pd.read_csv("/Users/danielm/Downloads/trip_level.csv")
final_dfs = final_dfs[final_dfs['consecutive_counts_y'].notna()]

def determine_time_data(time_stmp):
    date_object = datetime.strptime(time_stmp, "%Y%m%d %H:%M")
    week_day_dic = {0: 'monday', 1:'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'}
    day_of_week = date_object.weekday()
    for number, day in week_day_dic.items():
        if day_of_week == number:
            day_of_week = day
            break
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
    return day_time, day_of_week

final_dfs[['day_time', 'day_of_week']] = final_dfs['tmstmp'].apply(lambda x: pd.Series(determine_time_data(x)))

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
desired_columns = ['rt', 'day_time', 'day_of_week', 'ghost', 'consecutive_counts_y']
final_dfs = final_dfs[desired_columns]

# Compare schedule data with real data
def create_dict_delays(df_real_data, average_trip_duration):
    dict_delays = {}
    for _, observation in df_real_data.iterrows():
        route = observation["rt"]
        day_time = observation["day_time"]
        day = observation["day_of_week"]
        if observation["ghost"]:
            if route in dict_delays:
                dict_delays[route] += 30
            else:
                dict_delays[route] = 30
            continue
        expected_time = average_trip_duration.get((day, route, day_time), np.nan)
        delay = observation["consecutive_counts_y"] - expected_time
        if delay > 10:
            if route in dict_delays:
                dict_delays[route] += delay
            else:
                dict_delays[route] = delay
    return dict_delays

test = create_dict_delays(final_dfs, average_trip_duration)