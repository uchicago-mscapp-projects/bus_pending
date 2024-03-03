import pandas as pd
import pytest
from bus_pending.analysis.analysis import keep_last_and_first, calculate_trip_duration

# Values to test keep last and first function
columns_keep = ["trip_id", "weekday", "weekend", "arrival_time", "stop_id", "route_id"]
columns_results = ["trip_id", "weekday", "weekend", "arrival_time", "stop_id", "route_id"]

data_keep = [["350", True, False, "12:00:00", "fake_stop", "disney"],
             ["999", True, False, "15:00:00", "fake_stop2", "Uchicago"],
             ["102", False, True, "16:00:00", "fake_stop3", "Loop"],
             ["350", True, False, "12:15:00", "fake_stop", "disney"],
             ["999", True, False, "15:25:00", "fake_stop2", "Uchicago"],
             ["102",False, True, "16:20:00", "fake_stop3", "Loop"],
             ["350", True, False, "12:30:00", "fake_stop", "disney"],
             ["999", True, False, "15:50:00", "fake_stop2", "Uchicago"],
             ["102", False, True, "16:40:00", "fake_stop3", "Loop"],
             ["350", True, False, "12:45:00", "fake_stop", "disney"],
             ["999", True, False, "16:15:00", "fake_stop2", "Uchicago"],
             ["102", False, True, "17:00:00", "fake_stop3", "Loop"],
             ["350", True, False, "13:00:00", "fake_stop", "disney"],
             ["999", True, False, "16:40:00", "fake_stop2", "Uchicago"]]

data_results_keep = [["350", True, False, "12:00:00", "fake_stop", "disney", "13:00:00"],
                     ["999", True, False, "15:00:00", "fake_stop2", "Uchicago", "16:40:00"],
                     ["102", False, True, "16:00:00", "fake_stop3", "Loop", "17:00:00"]]


df_keep = pd.DataFrame(data_keep, columns= columns_keep)
results_keep = pd.DataFrame(data_results_keep, columns = columns_keep+["finish_time"])

# Values to test calculate trip duration
simple_case = pd.Timedelta(hours=4, minutes=30).total_seconds() / 60
negative_case = pd.Timedelta(hours=1, minutes=10).total_seconds() / 60


def test_keep_first_and_last():
    # Given the data we create, is simple to see what results we expect
    first_and_last = keep_last_and_first(df_keep)
    finish_time_102 = first_and_last.loc[first_and_last["trip_id"] == "102", "finish_time"]

    start_time_999 = first_and_last.loc[first_and_last["trip_id"] == "999", "start_time"]

    finish_time_350 = first_and_last.loc[first_and_last["trip_id"] == "350", "finish_time"]

    if not all(finish_time_102 == "17:00:00"):
        raise AssertionError("Function is not returning the correct finish time for trip_id 102")

    if not all(start_time_999 == "15:00:00"):
        raise AssertionError("Function is not returning the correct start time for trip_id 999")

    if not all(finish_time_350 == "13:00:00"):
        raise AssertionError("Function is not returning the correct finish time for trip_id 350")
    

def test_calculate_duration():
    actual_estimation = calculate_trip_duration(pd.Timedelta(hours=5), pd.Timedelta(hours=9, minutes=30))
    actual_estimation_2 = calculate_trip_duration(pd.Timedelta(hours=23, minutes=50), pd.Timedelta(hours=1))
    if not actual_estimation == simple_case:
        raise AssertionError(f"Actual estimation: {actual_estimation} is not equal to expected estimation: {simple_case}")
    if not actual_estimation_2 == negative_case:
        raise AssertionError(f"Actual estimation: {actual_estimation_2} is not equal to expected estimation: {negative_case}. Check cases with negative values!")
