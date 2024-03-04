import pandas as pd
from bus_pending.analysis.analyze_real_data import determine_time_data, find_ghost_buses

dic_test_determine = {
    "weekday": ("20240303 8:00", "morning", False),
    "weekend": ("20240301 20:00", "night", True),
}

columns_ghost = ["rt", "total_dist"]

data_ghost = [
    ["350", 1000],
    ["999", 2400],
    ["350", 1000],
    ["999", 2400],
    ["350", 1000],
    ["999", 2400],
    ["350", 1000],
    ["999", 10],
    ["350", 1000],
    ["999", 2400],
    ["350", 25],
    ["999", 2400],
    ["999", 2400],
    ["999", 2400],
]


df_ghost = pd.DataFrame(data_ghost, columns=columns_ghost)


def test_determine_time():
    for key, date in dic_test_determine.items():
        actual_day_time, actual_weekend = determine_time_data(date[0])
        expected_day_time = date[1]
        expected_weekend = date[2]
        if actual_day_time != expected_day_time:
            raise AssertionError(
                f"Expected day time {expected_day_time} does not match actual day time {actual_day_time}. Check your {key}"
            )
        if actual_weekend != expected_weekend:
            raise AssertionError(
                f"Expected weekend booleand {expected_weekend} does not mathc actual weekend boolean {actual_weekend}. Check your {key}"
            )


def test_find_ghost_buses():
    # From data provided, we know there should be 2 ghost buses
    mean_dist_route = df_ghost.groupby("rt")["total_dist"].mean()
    std_distance_route = df_ghost.groupby("rt")["total_dist"].std()
    print(mean_dist_route, std_distance_route)
    n = 0
    for _, observation in df_ghost.iterrows():
        if find_ghost_buses(observation, mean_dist_route, std_distance_route):
            n += 1
            print(n, observation)
    if n < 2:
        raise AssertionError(
            f"Expected ghost buses 2 are more than actual ghost buses {n}"
        )
    if n > 2:
        raise AssertionError(
            f"Expected ghost buses 2 are less than actual ghost buses {n}"
        )
