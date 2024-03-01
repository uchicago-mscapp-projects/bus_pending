import pandas as pd
import pytest
from analysis import analyze_schedule, keep_last_and_first, calculate_trip_duration

# Values to test keep last and first function
columns_keep = ["trip_id", "day", "arrival_time", "stop_id", "direction", "route_id"]
data_keep = [["350", "monday", "12:00:00", "fake_stop", "North", "disney"],
             ["999", "tuesday", "15:00:00", "fake_stop2", "South", "Uchicago"],
             ["350", "monday", "12:15:00", "fake_stop", "North", "disney"],
             ["999", "tuesday", "15:25:00", "fake_stop2", "South", "Uchicago"],
             ["350", "monday", "12:30:00", "fake_stop", "North", "disney"],
             ["999", "tuesday", "15:50:00", "fake_stop2", "South", "Uchicago"],
             ["350", "monday", "12:45:00", "fake_stop", "North", "disney"],
             ["999", "tuesday", "16:15:00", "fake_stop2", "South", "Uchicago"],
             ["350", "monday", "13:00:00", "fake_stop", "North", "disney"],
             ["999", "tuesday", "16:40:00", "fake_stop2", "South", "Uchicago"]]
data_results_keep = [["350", "monday", "12:00:00", "fake_stop", "North", "disney", "13:00:00"],
                     ["999", "tuesday", "15:00:00", "fake_stop2", "South", "Uchicago", "16:40:00"]]


df_keep = pd.DataFrame(data_keep, columns= columns_keep)
results_keep = pd.DataFrame(data_results_keep, columns = columns_keep+["finish_time"])

# Values to test calculate trip duration
simple_case = pd.Timedelta(hours=4, minutes=30)
negative_case = pd.Timedelta(hours=1, minutes=10)


def test_keep_last():
    # Given the data we create, is simple to see what results we expect
    first_and_last = keep_last_and_first(data_keep)
    if not first_and_last == data_results_keep:
        raise AssertionError("Function is not returning only the first and last observation of every trip")
    


    
