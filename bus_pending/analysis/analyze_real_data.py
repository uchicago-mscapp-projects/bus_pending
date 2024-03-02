import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import re

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
print(final_dfs.head())