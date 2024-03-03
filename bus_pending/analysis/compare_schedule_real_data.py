import pandas as pd
import numpy as np
from analysis.analyze_real_data import do_analysis
from analysis.analysis import analyze_schedule

filename = '/Users/danielm/Downloads/buses_static_2024-02-29.db'
query_sch = """
SELECT schedule.*, trips.route_id, trips.direction, calendar.*
FROM schedule
LEFT JOIN trips ON schedule.trip_id = trips.trip_id
LEFT JOIN calendar ON trips.service_id = calendar.service_id
ORDER BY schedule.arrival_time;
"""
seconds_in_day = 86400

final_dfs = pd.read_csv("/Users/danielm/Downloads/trip_level.csv")
avg_trip_weekend, avg_trip_weekday = analyze_schedule(filename, query_sch)
final_dfs = do_analysis(final_dfs)


def estimate_delay(df_real_data, avg_trip_weekday, avg_trip_weekend):
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

estimate_delay(final_dfs, avg_trip_weekday, avg_trip_weekend)

final_dfs.to_csv("")